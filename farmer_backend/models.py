import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import os
import time 

load_dotenv()

class farmer_db:
    def __init__(self, conn_params):
        attempts = 5
        while attempts:
            try:
                self.conn = psycopg2.connect(**conn_params)
                break
            except psycopg2.OperationalError as e:
                attempts -= 1
                print("Postgres not ready, retrying in 10 seconds...")
                time.sleep(10)
        else:
            raise Exception("Could not connect to Postgres after multiple attempts")
        self._create_tables()
    
    def _create_tables(self):
        with self.conn.cursor() as cursor:
            self.conn.autocommit = True
            try:
                cursor.execute('''
                    DO $$ 
                    BEGIN 
                        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pgcrypto') THEN
                            CREATE EXTENSION pgcrypto;
                        END IF;
                    END $$;
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS public.users (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        "name" TEXT,
                        "role" TEXT,
                        "longtitude" FLOAT,
                        "latitude" FLOAT,
                        "location" TEXT,
                        "crops" TEXT[],
                        'additional_info' TEXT
                    );
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS public.conversations (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        conversation JSONB
                    );
                ''')

                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS public.api_data (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        "weather_forecast" TEXT,
                        "heat_stress" TEXT,
                        "soil_moisture" TEXT,
                        "frost_prediction" TEXT,
                        "hydric_stress" TEXT,
                        "drone_flight_suggestions" TEXT
                    );
                ''')

                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS public.community (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        "title" TEXT,
                        "description" TEXT,
                        "image" TEXT,
                        "likes" INT,
                        "comments" JSONB
                    );
                ''')

                cursor.execute('''
    CREATE TABLE IF NOT EXISTS public.users (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        "name" TEXT,
        "role" TEXT,
        "longtitude" FLOAT,
        "latitude" FLOAT,
        "location" TEXT,
        "crops" TEXT[],
        "additional_info" TEXT
    );
''')

            except Exception as e:
                print("Error creating tables:", e)
            finally:
                self.conn.autocommit = False


    def get_users(self):
        try:
            with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT * FROM public.users")
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            self.conn.rollback()
            raise e

    def insert_users(self, name, role, longtitude, latitude, location, crops, additional_info):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute('''
                    INSERT INTO public.users (name, role, longtitude, latitude, location, crops, additional_info)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id;
                ''', (name, role, longtitude, latitude, location, crops, additional_info))
                new_id = cursor.fetchone()[0]
            self.conn.commit()
            return new_id
        except Exception as e:
            self.conn.rollback()
            raise e

    def update_users(self, id, name, role, longtitude, latitude, location, crops, additional_info):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute('''
                    UPDATE public.users
                    SET name = %s, role = %s, longtitude = %s, latitude = %s, location = %s, crops = %s, additional_info = %s
                    WHERE id = %s
                ''', (name, role, longtitude, latitude, location, crops, additional_info, id))
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            self.conn.rollback()
            raise e

    def delete_users(self, id):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute('''
                    DELETE FROM public.users WHERE id = %s
                ''', (id,))
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            self.conn.rollback()
            raise e

    def get_user_by_id(self, id):
        try:
            with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT * FROM public.users WHERE id = %s", (id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            self.conn.rollback()
            raise e

    def insert_chat_conversation(self, conversation):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute('''
                    INSERT INTO public.conversations (conversation)
                    VALUES (%s)
                    RETURNING id;
                ''', (psycopg2.extras.Json(conversation),))
                new_id = cursor.fetchone()[0]
            self.conn.commit()
            return new_id
        except Exception as e:
            self.conn.rollback()
            raise e
        
    def insert_community(self, title, description, image, likes, comments):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute('''
                    INSERT INTO public.community (title, description, image, likes, comments)
                    VALUES (%s, %s, %s, %s, %s) 
                    RETURNING id;
                ''', (title, description, image, likes, psycopg2.extras.Json(comments)))
                new_id = cursor.fetchone()[0]
            self.conn.commit()
            return new_id
        except Exception as e:
            self.conn.rollback()
            raise e
    
    def get_community_by_id(self, id):
        try:
            with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT * FROM public.community WHERE id = %s", (id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            self.conn.rollback()
            raise e

    def update_community(self, id, title, description, image, likes, comments):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute('''
                    UPDATE public.community
                    SET title = %s, description = %s, image = %s, likes = %s, comments = %s
                    WHERE id = %s
                ''', (title, description, image, likes, psycopg2.extras.Json(comments), id))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e

    def delete_community_by_id(self, id):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("DELETE FROM public.community WHERE id = %s", (id,))
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            self.conn.rollback()
            raise e
    
    def get_all_community_posts(self):
        try:
            with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT * FROM public.community")
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            self.conn.rollback()
            raise e
        
    def get_all_chat_conversations(self):
        try:
            with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT * FROM public.conversations")
                rows = cursor.fetchall()
                return [dict(row) for row in rows]  # Convert to JSON format
        except Exception as e:
            self.conn.rollback()
            raise e
            
    def update_chat_conversation(self, id, conversation):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute('''
                    UPDATE public.conversations
                    SET conversation = %s
                    WHERE id = %s
                ''', (psycopg2.extras.Json(conversation), id))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e
            
    def get_chat_conversation_by_id(self, id):
        try:
            with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT * FROM public.conversations WHERE id = %s", (str(id),))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            self.conn.rollback()
            raise e

    def get_api_data(self):
        self.conn.autocommit = True
        try:
            with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT question_text FROM public.api_data")
                rows = cursor.fetchall()
                return [row["question_text"] for row in rows]
        except Exception as e:
            self.conn.rollback()
            raise e
        
    def insert_api_data(self, weather_forecast, heat_stress, soil_moisture, frost_prediction, hydric_stress, drone_flight_suggestions):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute('''
                    INSERT INTO public.api_data (weather_forecast, heat_stress, soil_moisture, frost_prediction, hydric_stress, drone_flight_suggestions)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id;
                ''', (weather_forecast, heat_stress, soil_moisture, frost_prediction, hydric_stress, drone_flight_suggestions))

                new_id = cursor.fetchone()[0]
            self.conn.commit()
            return new_id
        except Exception as e:
            self.conn.rollback()
            raise e

    def get_api_data_by_id(self, id):
        try:
            with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT question_text FROM public.api_data WHERE id = %s", (id,))
                row = cursor.fetchone()
                return row["question_text"] if row else None
        except Exception as e:
            self.conn.rollback()
            raise e


    def update_api_data(self, weather_forecast, heat_stress, soil_moisture, frost_prediction, hydric_stress, drone_flight_suggestions):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute('''
                    UPDATE public.api_data
                    SET weather_forecast = %s, heat_stress = %s, soil_moisture = %s, frost_prediction = %s, hydric_stress = %s, drone_flight_suggestions = %s
                    WHERE id = %s
                ''', (weather_forecast, heat_stress, soil_moisture, frost_prediction, hydric_stress, drone_flight_suggestions))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e

    def delete_api_data_by_id(self, id):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("DELETE FROM public.api_data WHERE id = %s", (id,))
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            self.conn.rollback()
            raise e


db_params = {
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT")
}

print(db_params)

my_farmer_db = farmer_db(db_params)


