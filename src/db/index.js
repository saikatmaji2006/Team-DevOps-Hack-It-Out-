import mongoose from "mongoose";
import { DB_Name } from "../constants.js";
const connectDB = async () => {
    try {
      const conn = await mongoose.connect(
        "mongodb+srv://saikat:1234@cluster0.gntgr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        
      );
  
      console.log(`MongoDB Connected: ${conn.connection.host}`);
      console.log(`Database Name: ${conn.connection.name}`);
    } catch (error) {
      console.error(`Error connecting to MongoDB: ${error.message}`);
      process.exit(1); // Exit process with failure
    }
  };
  
export default connectDB