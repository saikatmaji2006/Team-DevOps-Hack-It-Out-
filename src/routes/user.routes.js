import { Router } from "express";
import { registerUser,loginUser,logoutUser } from "../controllers/user.controller.js";
import { getGeolocation } from "../controllers/location.controller.js";
import { upload } from "../middlewares/multer.middleware.js";
import { asyncHandler } from "../utils/asyncHandler.js";
import { verifyJWT } from "../middlewares/authorisation.js";
import { mintNFT, getTokenURI, isEducator, grantEducator } from "../controllers/eduquestController.js";


const router = Router()
router.route("/register").post(
    upload.fields([
        {
            name : "avatar",
            maxCount : 1
        },
        {
            name : "coverImage",
            maxCount : 1
            
        },
    ]),
    registerUser)
router.route("/loginUser").post(loginUser)
router.route("/getLocation").post(asyncHandler(async (req, res) => {
    const { latitude, longitude } = req.body;
    const locationData = await getGeolocation(latitude, longitude);
    res.json(locationData);
}));
router.post("/mint-nft", mintNFT);
router.get("/token-uri/:tokenId", getTokenURI);
router.get("/is-educator/:address", isEducator);
router.post("/grant-educator", grantEducator);


router.route("/logout").post(verifyJWT ,logoutUser)

export default router