
import ee
import geemap
import os

# ==========================================================
# 1. AUTHENTICATION
# ==========================================================

ee.Authenticate()
ee.Initialize(project="ecosensingcalculator")


# ==========================================================
# 2. DEFINE STUDY AREA
# ==========================================================

area = ee.Geometry.Rectangle([
    -60.5, -3.5,
    -59.5, -2.5
])


# ==========================================================
# 3. DATE RANGE
# ==========================================================

data_inicio = "2025-06-01"
data_fim = "2025-09-01"


# ==========================================================
# 4. LOAD SENTINEL-2 DATASET
# ==========================================================

colecao = (
    ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
    .filterBounds(area)
    .filterDate(data_inicio, data_fim)
    .filter(
        ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 30)
    )
)


# ==========================================================
# 5. CLOUD MASK
# ==========================================================

def remover_nuvens(imagem):

    qa = imagem.select("QA60")

    nuvens = 1 << 10
    cirrus = 1 << 11

    mascara = (
        qa.bitwiseAnd(nuvens).eq(0)
        .And(qa.bitwiseAnd(cirrus).eq(0))
    )

    return imagem.updateMask(mascara)


colecao = colecao.map(remover_nuvens)


# ==========================================================
# 6. CALCULATE NDVI
# ==========================================================

def calcular_ndvi(imagem):

    ndvi = imagem.normalizedDifference(
        ["B8", "B4"]
    ).rename("NDVI")

    return ndvi.copyProperties(
        imagem, ["system:time_start"]
    )


ndvi_colecao = colecao.map(calcular_ndvi)


# ==========================================================
# 7. MEDIAN COMPOSITE
# ==========================================================

ndvi_mediano = ndvi_colecao.median().clip(area)


# ==========================================================
# 8. REGIONAL STATISTICS
# ==========================================================

estatisticas = ndvi_mediano.reduceRegion(
    reducer=(
        ee.Reducer.mean().combine(
            reducer2=ee.Reducer.minMax(),
            sharedInputs=True
        )
    ),
    geometry=area,
    scale=10,
    maxPixels=1e9
)

print("Number of images:", colecao.size().getInfo())
print("NDVI statistics:", estatisticas.getInfo())


# ==========================================================
# 9. VISUALIZATION
# ==========================================================

mapa = geemap.Map()

mapa.centerObject(area, 9)

mapa.addLayer(
    ndvi_mediano,
    {
        "min": -0.2,
        "max": 0.9,
        "palette": [
            "8c510a",
            "d8b365",
            "f6e8c3",
            "c7eae5",
            "5ab4ac",
            "01665e",
            "003c30"
        ]
    },
    "NDVI Median"
)

mapa.addLayer(
    area,
    {"color": "red"},
    "Study Area"
)


# ==========================================================
# 10. DOWNLOAD GEOTIFF LOCALLY
# ==========================================================

output_dir = "./data"

os.makedirs(output_dir, exist_ok=True)

output_file = os.path.join(
    output_dir,
    "NDVI_Amazonia_2025.tif"
)

geemap.download_ee_image(
    image=ndvi_mediano,
    filename=output_file,
    region=area,
    scale=10,
    crs="EPSG:4326"
)

print("Download completed!")
print("File saved at:", os.path.abspath(output_file))


# ==========================================================
# 11. DISPLAY MAP
# ==========================================================

mapa
