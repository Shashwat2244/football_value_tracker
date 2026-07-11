import duckdb

# --- Configuration ---
MOTHERDUCK_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InNoYXNod2F0c2hyaXZhc3RhdmEyMDAzQGdtYWlsLmNvbSIsIm1kUmVnaW9uIjoiYXdzLWV1LWNlbnRyYWwtMSIsInNlc3Npb24iOiJzaGFzaHdhdHNocml2YXN0YXZhMjAwMy5nbWFpbC5jb20iLCJwYXQiOiJYNHNCNzJCcDBFbk1hVDRWa0tNbEVKX3ZYNkNMNnB2M0xCSno5YUF5Mm1BIiwidXNlcklkIjoiZmFkNGFlMjctN2I4Ni00YmNiLWEzYTktNTM5OGQyYjNlMmIzIiwiaXNzIjoibWRfcGF0IiwicmVhZE9ubHkiOmZhbHNlLCJ0b2tlblR5cGUiOiJyZWFkX3dyaXRlIiwiaWF0IjoxNzgzNzY4MTUyfQ.sTQ_BJPYer0Fvdw-7-hYNSnpTWhchGl908pRs89PZHc"

# Ensure this matches the EXACT name of the file you generated in Phase 1
PARQUET_FILE = "premier_league_values_2026-07-11.parquet" 

def load_data_to_cloud():
    print("Connecting to MotherDuck Cloud...")
    
    # 1. Connect to the default MotherDuck environment (notice we removed 'football_analytics' here)
    con = duckdb.connect(f'md:?motherduck_token={MOTHERDUCK_TOKEN}')
    
    # 2. Safely create the database (if it doesn't already exist)
    print("Ensuring database 'football_analytics' exists...")
    con.execute("CREATE DATABASE IF NOT EXISTS football_analytics;")
    
    # 3. Tell DuckDB to use this specific database for all following commands
    con.execute("USE football_analytics;")
    
    print(f"Uploading {PARQUET_FILE} to cloud data warehouse...")
    
    # 4. Create the table and load the Parquet data
    con.execute(f"""
        CREATE OR REPLACE TABLE stg_market_values AS 
        SELECT * FROM '{PARQUET_FILE}'
    """)
    
    print("\n--- Upload Complete! Verifying Data in the Cloud ---")
    
    query = """
        SELECT 
            club, 
            COUNT(player_name) as squad_size,
            SUM(market_value_eur) as total_squad_value
        FROM stg_market_values 
        GROUP BY club
        ORDER BY total_squad_value DESC
        LIMIT 5;
    """
    
    result_df = con.execute(query).df()
    print(result_df)
    
    con.close()
    print("\nConnection closed. Check your MotherDuck UI!")

if __name__ == "__main__":
    load_data_to_cloud()