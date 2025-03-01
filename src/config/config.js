import dotenv from "dotenv"
import { ethers } from "ethers";
import { env } from "process" ;
dotenv.config({
    path: '..\..\.env'
})


// Load environment variables
const RPC_URL = process.env.EDUCHAIN_RPC_URL;
const PRIVATE_KEY = process.env.PRIVATE_KEY;
const CONTRACT_ADDRESS = process.env.CONTRACT_ADDRESS;

// Import ABI
import { readFileSync } from "fs";
const contractJSON = JSON.parse(readFileSync("../eduquest-backend/artifacts/contracts/EduQuest.sol/EduQuest.json", "utf-8"));
const contractABI = contractJSON.abi;

// Initialize provider and wallet
const provider = new ethers.JsonRpcProvider(RPC_URL);
const wallet = new ethers.Wallet(PRIVATE_KEY, provider);

// Initialize contract instance
export const eduQuestContract = new ethers.Contract(CONTRACT_ADDRESS, contractABI, wallet);

// module.exports = { eduQuestContract };
