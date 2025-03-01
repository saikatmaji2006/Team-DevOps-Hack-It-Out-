
import {asyncHandler}  from "../utils/asyncHandler.js";
import {ApiError} from "../utils/ApiError.js";
import { user } from "../models/user.model.js";
import { UploadOnCloudinary } from "../utils/cloudinary.js";
import {ApiResponse} from "../utils/ApiResponse.js";
import mongoose from "mongoose";
const generateAccessAndRefreshToken = async (userId) => {
    //now generateAccessToken and refreshToken
    try {
        const User = await user.findById(userId)
        if (!User) {
            throw new ApiError(404, "User not found");
        }
    
        const accessToken = User.generateAccessToken()
        const refreshToken = User.generateRefreshToken()
        User.refreshToken = refreshToken;
        await User.save({validateBeforeSave : false})
        console.log(accessToken,refreshToken);
        return {
            accessToken,
            refreshToken
        };
        
        
    } catch (error) {
        throw new ApiError(500, "problem is here");
        
    }

}
const registerUser = asyncHandler( async(req,res)=>{
    const {fullName,Email, UserName, password}=req.body
    console.log("Email: ",Email,"\n","password: ",password);
    if([fullName,Email, UserName, password].some((field)=>
    field?.trim() === "")
){
    throw new ApiError(400,"all fields are required");
    
}
    const existedUser = await user.findOne({
        $or: [{UserName},{Email}]
    })
    if(existedUser) {
        throw new ApiError(409,"UserName or Email already exists")
        
    }
    const avatarLocalPath = await req.files?.avatar?.[0]?.path;
    const coverImageLocalPath = await req.files?.coverImage?.[0]?.path;
    console.log(avatarLocalPath);
    
    if(!avatarLocalPath){
        throw new ApiError(400,"Avatar File 1 is required")
    }
    const avatar = await UploadOnCloudinary(avatarLocalPath)
    const coverImage = await UploadOnCloudinary(coverImageLocalPath)
    let coverImageurl = "";
    if(coverImage?.url){
        coverImageurl = coverImage.url

    }
    if(!avatar){
        throw new ApiError(400,"Avatar File 2 is Required")
    }
    const newuser = await user.create({
        fullName,
        avatar : avatar.url,
        coverImage: coverImageurl,
        Email,
        password,
        UserName: UserName.toLowerCase()

    })
    .then (console.log("user created"));
    const createdUser = await user.findById(newuser._id).select(
        "-password -refreshToken"
    )

    if (!createdUser) {
        throw new ApiError(500, "Something went wrong while registering the user")
    }
    return res.status(201).json(
        new ApiResponse(200,createdUser,"user registered succesfully")
    )

})

const loginUser = asyncHandler( async(req,res)=>{
    const{UserName,password,Email}=req.body;
    if(!Email && !UserName)
        {throw new ApiError(400,"enter username or email to continue");}
    if(password=="")
       { throw new ApiError(400,"enter your password");}
    const existedUser = await user.findOne({
        $or: [{UserName},{Email}]
    })
    if(!existedUser) {
        throw new ApiError(409,"User donot exist")
        
    }

    const isPasswordCorrect = await existedUser.isPasswordCorrect(password)
    if(!isPasswordCorrect){
        throw new ApiError(401,"invalid user credentials")
    }
    const loginUser = existedUser
    console.log("       a");

    const { accessToken, refreshToken } = await generateAccessAndRefreshToken(loginUser._id);
    if (!accessToken || !refreshToken) {
        throw new ApiError(500, "Failed to generate authentication tokens");
    }
    
    console.log(accessToken,refreshToken);
    const option = {
        
    }
    return res
    .status(200)
    .cookie("accessToken",accessToken,option)
    .cookie("refreshToken",refreshToken,option)
    .json(
        new ApiResponse (200,{user:loginUser,accessToken,refreshToken},"User Logged in succesfully")
    )

})
const logoutUser = async(req,res)=>{
    await user.findByIdAndUpdate(
        req.user._id,
        {
            $unset: {
                refreshToken: 1 // this removes the field from document
            }
        },
        {
            new: true
        }
    )
    return res
    .status(200)
    .clearCookie("accessToken")
    .clearCookie("refreshToken")
    .json(
        new ApiResponse(200,{},"user logged out successfully")
    )
}
export{loginUser,registerUser,logoutUser};


//logic
//take input UserName Email fullname avatar password
//check whether UserName and Email are unique and avatar password is there
//remove password and refreshToken field from response
//upload the info to mongodb once the conditions are met
//once it is uploaded take the avatar link and use multer to to upload to cloudinary allong with storing a local copy
//once all stuff are done route to login page
 