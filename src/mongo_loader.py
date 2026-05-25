def dataframe_to_mongo_documents(df_clean):
    documentos_mongo = []
    for _, row in df_clean.iterrows():
        doc = {
            "location": {
                "type": "Point",
                "coordinates": [row["Longitude"], row["Latitude"]],
            },
            "features": {
                "NDVI": float(row["NDVI"]),
                "NDBI": float(row["NDBI"]),
                "Distance_to_Water_m": float(row["D2W_meters"]),
            },
            "target": {"LST_Celsius": float(row["LST_Target"])},
        }
        documentos_mongo.append(doc)
    return documentos_mongo


def insert_documents_in_batches(collection, documentos_mongo, batch_size=10000):
    for index in range(0, len(documentos_mongo), batch_size):
        batch = documentos_mongo[index : index + batch_size]
        collection.insert_many(batch)
        print(f"  -> Insertados {index + len(batch)} de {len(documentos_mongo)} documentos...")
