import NodeGeocoder from 'node-geocoder';


// Configure the geocoder


// Function to get geolocation based on coordinates
const getGeolocation = async (latitude, longitude) => {
    const options = {
        provider: 'openstreetmap', // You can use other providers like 'google', 'mapquest', etc.
    };
      
    const geocoder = NodeGeocoder(options);
  try {
    const res = await geocoder.reverse({ lat: latitude, lon: longitude });
    if (res.length > 0) {
      return {
        latitude: res[0].latitude,
        longitude: res[0].longitude,
        formattedAddress: res[0].formattedAddress,
        city: res[0].city,
        state: res[0].state,
        country: res[0].country,
        zipcode: res[0].zipcode
      };
    } else {
      return { error: 'No results found' };
    }
  } catch (error) {
    console.error('Error fetching location:', error);
    return { error: 'Error fetching location' };
  }
};
export {getGeolocation};