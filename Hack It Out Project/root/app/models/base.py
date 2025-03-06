import uuid
import json
import hashlib
from datetime import datetime
from typing import Any, Dict, TypeVar, Type, Optional, ClassVar, List, Set, Union, Callable

from bson import ObjectId
from mongoengine import Document, StringField, DateTimeField, IntField, DictField, ListField, signals
from mongoengine.base.fields import BaseField
from pymongo import IndexModel, ASCENDING, DESCENDING

from app.services.cache import get_cache_service

T = TypeVar('T', bound='BaseDocument')

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class BaseDocument(Document):
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    version = IntField(default=1, min_value=1)
    
    created_by = StringField(max_length=255)
    updated_by = StringField(max_length=255)
    is_deleted = StringField(default=False)
    
    _cache_hash = StringField()
    _cache_ttl = 3600
    
    _changed_fields: Set[str] = set()
    _initial_data: Dict[str, Any] = {}
    
    meta: ClassVar[Dict[str, Any]] = {
        'abstract': True,
        'ordering': ['-created_at'],
        'indexes': [
            IndexModel([('created_at', DESCENDING)]),
            IndexModel([('updated_at', DESCENDING)]),
            {'fields': ['is_deleted']}
        ],
        'strict': False
    }
    
    def __init__(self, *args, **kwargs):
        self._changed_fields = set()
        super().__init__(*args, **kwargs)
        self._initial_data = self.to_mongo().to_dict()
    
    def save(self, *args, **kwargs):
        user_id = kwargs.pop('user_id', None)
        skip_hooks = kwargs.pop('skip_hooks', False)
        
        self.updated_at = datetime.utcnow()
        self.version += 1
        
        if user_id:
            if not self.id:
                self.created_by = user_id
            self.updated_by = user_id
        
        self._cache_hash = self._calculate_hash()
        
        result = super().save(*args, **kwargs)
        
        if not skip_hooks:
            self._invalidate_cache()
            
        self._initial_data = self.to_mongo().to_dict()
        self._changed_fields = set()
        
        return result
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if key in self._fields:
                setattr(self, key, value)
                self._changed_fields.add(key)
        
        return self.save()
    
    def delete(self, user_id=None):
        self.is_deleted = True
        self.updated_at = datetime.utcnow()
        if user_id:
            self.updated_by = user_id
        return self.save(skip_hooks=False)
    
    def hard_delete(self):
        self._invalidate_cache()
        return super().delete()
    
    @classmethod
    async def get_by_id(cls: Type[T], id: str, use_cache: bool = True) -> Optional[T]:
        if not use_cache:
            return cls.objects(id=id, is_deleted=False).first()
        
        cache = await get_cache_service()
        cache_key = f"{cls.__name__}:{id}"
        
        cached_data = await cache.get(cache_key)
        if cached_data:
            return cls.from_json(cached_data)
        
        document = cls.objects(id=id, is_deleted=False).first()
        if document:
            await cache.set(
                cache_key, 
                document.to_json(),
                expiration=document._cache_ttl
            )
        
        return document
    
    @classmethod
    def get_all(cls: Type[T], include_deleted: bool = False) -> List[T]:
        query = {} if include_deleted else {'is_deleted': False}
        return list(cls.objects(**query))
    
    def to_dict(self, exclude: List[str] = None) -> Dict[str, Any]:
        exclude = exclude or []
        exclude = set(exclude + ['_cache_hash', '_cls'])
        
        data = self.to_mongo().to_dict()
        return {k: v for k, v in data.items() if k not in exclude}
    
    def to_json(self, exclude: List[str] = None) -> str:
        return json.dumps(self.to_dict(exclude), cls=JSONEncoder)
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        return cls(**{k: v for k, v in data.items() if k in cls._fields or k == 'id'})
    
    def get_changed_fields(self) -> Dict[str, Any]:
        current_data = self.to_mongo().to_dict()
        changes = {}
        
        for field_name, current_value in current_data.items():
            if field_name in self._initial_data:
                initial_value = self._initial_data[field_name]
                if current_value != initial_value:
                    changes[field_name] = current_value
            else:
                changes[field_name] = current_value
                
        return changes
    
    def _calculate_hash(self) -> str:
        data_str = json.dumps(self.to_dict(exclude=['updated_at', 'version']), 
                             sort_keys=True, cls=JSONEncoder)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    async def _invalidate_cache(self) -> None:
        cache = await get_cache_service()
        cache_key = f"{self.__class__.__name__}:{self.id}"
        await cache.delete(cache_key)
    
    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        pass
    
    @classmethod
    def post_save(cls, sender, document, **kwargs):
        pass
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.id}>"

signals.pre_save.connect(BaseDocument.pre_save)
signals.post_save.connect(BaseDocument.post_save)