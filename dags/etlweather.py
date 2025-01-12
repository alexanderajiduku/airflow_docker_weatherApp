from airflow import DAG
from airflow.providers.http.hooks.http import HttpHook
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.decorators import task
from airflow.utils.dates import days_ago


LATITUDE = "64.7524"
LONGITUDE = "21.0403"
POSTGRES_CONN_ID = "postgres_default"
API_CONN_ID = "open_meteo_api"


default_args = {
    "owner": "airflow",
    "start_date": days_ago(1),
}


# Create a DAG

with DAG(
    dag_id="weather_etl_pipeline",
    default_args=default_args,
    schedule_interval="*/10 * * * *",  # Changed to run every minute
    catchup=False,
) as dag:

    @task()
    def check_connection():
        """Check if the Open Meteo API is reachable"""
        http_sensor = HttpSensor(
            task_id="check_api_connection",
            http_conn_id=API_CONN_ID,
            endpoint=f"/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&current_weather=true",
            response_check=lambda response: response.status_code == 200,
            poke_interval=5,
            timeout=20,
        )
        http_sensor.poke(context={})
        return True

    @task()
    def extract_weather_data(check_connection):
        """Extract weather from Open Meteo API airflow connection"""
        http_hook = HttpHook(http_conn_id=API_CONN_ID, method="GET")
        endpoint = f"/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&current_weather=true"
        response = http_hook.run(endpoint)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch weather data: {response.status_code}")

    @task()
    def transform_weather_data(weather_data):
        """Transform the weather data to JSON format"""
        current_weather = weather_data["current_weather"]
        transformed_data = {
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
            "temperature": current_weather["temperature"],
            "windspeed": current_weather["windspeed"],
            "winddirection": current_weather["winddirection"],
            "weathercode": current_weather["weathercode"],
        }
        return transformed_data

    @task()
    def load_weather_data(transformed_data):
        """Load the data into PostgreSQL DB"""
        pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
        conn = pg_hook.get_conn()
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_data (
            latitude FLOAT,
            longitude FLOAT,
            temperature FLOAT,
            windspeed FLOAT,
            winddirection FLOAT,
            weathercode INT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute(
            """
        INSERT INTO weather_data (latitude, longitude, temperature, windspeed, winddirection, weathercode)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
            (
                transformed_data["latitude"],
                transformed_data["longitude"],
                transformed_data["temperature"],
                transformed_data["windspeed"],
                transformed_data["winddirection"],
                transformed_data["weathercode"],
            ),
        )

        conn.commit()
        cursor.close()

    check_connection = check_connection()
    weather_data = extract_weather_data(check_connection)
    transformed_data = transform_weather_data(weather_data)
    load_weather_data(transformed_data)
