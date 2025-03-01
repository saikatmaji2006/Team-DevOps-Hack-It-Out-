import mongoose from "mongoose";
import jwt from "jsonwebtoken";
import bcrypt from "bcrypt";
const userSchema = new mongoose.Schema({
    UserName : {
        type : String,
        required : true,
        unique : true,
        lowercase : true,
        trim : true,
        index: true,

    },
    Email : {
        type : String,
        required : true,
        unique : true,
        lowercase : true,
        trim : true,
        

    },
    linkedIn : {
        type : String,
        // required : true,
        unique : true,
        trim : true,
        

    },
    gitHUb : {
        type : String,
        required : true,
        unique : true,
        
        trim : true,
        

    },
    x : {
        type : String,
        // required : true,
        unique : true,
        trim : true,
        

    },country : {
        type : String,
        required : true,
        unique : true,
        lowercase : true,
        trim : true,
        

    },
    
    reputationRanking : {
        type : Number,
        //required : true,
        unique : true,
        lowercase : true,
        trim : true,
        

    },
    day : {
        type : Number,
        //required : true,
        unique : true,
        lowercase : true,
        trim : true,
        

    },
    leetCode : {
        type : String,
        required : true,
        unique : true,
        
        trim : true,
        

    },
    fullName : {
        type : String,
        required : true,
        trim : true,//linked github x country reputationranking day nft-points
        index: true,

    },
    avatar : {
        type : String, // cloudinary url
        required : true
    },
    coverImage : {
        type : String,
    },
    
    password : {
        type : String,
        required : [true,"the password is required"]
    },
    refreshToken : {
        type : String,
    }
},
{
    timestamps : true,
})
userSchema.pre("save", async function (next) {
    if(this.isModified("password")){
    this.password = await bcrypt.hash(this.password,11);
    next()
    }
})
userSchema.methods.isPasswordCorrect = async function 
(password) {
   return await bcrypt.compare(password,this.password)
}
userSchema.methods.generateAccessToken = function(){
    return jwt.sign(
        {
            _id : this._id,
            Email : this.Email,
            UserName : this.UserName,
            fullName : this.fullName,


        },
        process.env.ACCESS_TOKEN_SECRET,
        {
            expiresIn: process.env.ACCESS_TOKEN_EXPIRY,
        }

    )
}
userSchema.methods.generateRefreshToken = function(){
    return jwt.sign(
        {
            _id : this._id,
           

        },
        process.env.REFRESH_TOKEN_SECRET,
        {
            expiresIn: process.env.REFRESH_TOKEN_EXPIRY,
        }

    )
}
export const user = mongoose.model("user",userSchema)