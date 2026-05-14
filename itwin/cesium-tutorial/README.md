# iTwin + Cesium Introduction Tutorial App

This repository contains the starter code used in the [iTwin + Cesium Introduction tutorial series](https://cesium.com/learn/), along with completed code examples for each tutorial.

Have questions? Ask them on the [community forum](https://community.cesium.com).

Found a bug? Open an [issue](https://github.com/iTwin/itwin-cesium-tutorial-app/issues).

## 🚀 Using the Tutorial Starter Code (main branch)

1. Clone the repository  
2. Rename `.env.example` to `.env`  
3. Add your own [Cesium ion access token](https://ion.cesium.com/tokens) 
4. Run `npm install`  
5. Start the app with `npm run dev`  
6. Open `http://localhost:5173` in your browser

## 🔍 Using the Completed Tutorial Code (tutorial branches)

1. Clone the repository  
2. Switch to the branch for the completed tutorial you want to view (e.g., `tutorial-2-complete`)  
3. Use the provided `.env` file — it contains credentials for accessing example content  
4. Run `npm install`  
5. Start the app with `npm run dev`  
6. Open `http://localhost:5173` in your browser

## 🔧 Maintenance Guidelines

- **Environment Settings**  
  - The **main branch** should **not** contain any committed `.env` credentials.  
  - **Tutorial branches** may include `.env` files with approved credentials for accessing example content.  
    - If you modify these credentials locally, ensure that **personal credentials are not accidentally committed**.

- **Credential Rotation**  
  Credentials should be **regenerated every two months**.


## :green_book:License

[Apache 2.0](http://www.apache.org/licenses/LICENSE-2.0.html). The iTwin + Cesium Introduction Tutorial App is free to use as starter project for both commercial and non-commercial use.

## 👥Contributions
Pull requests are appreciated. Please use the same [Contributor License Agreement (CLA)](https://github.com/CesiumGS/cesium/blob/master/CONTRIBUTING.md) used for [Cesium](https://cesium.com/).
