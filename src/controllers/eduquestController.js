import { eduQuestContract } from "../config/config.js";
// 🎯 Mint an NFT
export const mintNFT = async (req, res) => {
    try {
        const { recipient, tokenURI } = req.body;

        if (!recipient || !tokenURI) {
            return res.status(400).json({ error: "Recipient and Token URI are required" });
        }

        const tx = await eduQuestContract.safeMint(recipient, tokenURI);
        await tx.wait();

        res.json({ success: true, txHash: tx.hash });
    } catch (error) {
        console.error("Minting error:", error);
        res.status(500).json({ error: error.message });
    }
};

// 🎯 Get Token URI
export const getTokenURI = async (req, res) => {
    try {
        const tokenId = req.params.tokenId;
        const tokenURI = await eduQuestContract.tokenURI(tokenId);
        res.json({ tokenId, tokenURI });
    } catch (error) {
        console.error("Error fetching token URI:", error);
        res.status(500).json({ error: error.message });
    }
};

// 🎯 Check if Address is Educator
export const isEducator = async (req, res) => {
    try {
        const address = req.params.address;
        const hasRole = await eduQuestContract.hasRole(
            ethers.keccak256(ethers.toUtf8Bytes("EDUCATOR_ROLE")),
            address
        );

        res.json({ address, isEducator: hasRole });
    } catch (error) {
        console.error("Error checking educator role:", error);
        res.status(500).json({ error: error.message });
    }
};

// 🎯 Grant Educator Role
export const grantEducator = async (req, res) => {
    try {
        const { educatorAddress } = req.body;

        if (!educatorAddress) {
            return res.status(400).json({ error: "Educator address is required" });
        }

        const tx = await eduQuestContract.grantRole(
            ethers.keccak256(ethers.toUtf8Bytes("EDUCATOR_ROLE")),
            educatorAddress
        );
        await tx.wait();

        res.json({ success: true, txHash: tx.hash });
    } catch (error) {
        console.error("Error granting educator role:", error);
        res.status(500).json({ error: error.message });
    }
};

// Export functions
//export { mintNFT, getTokenURI , isEducator, grantEducator };