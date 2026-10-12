import math
import sqlite3

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import cartopy.crs as ccrs


class DBMap:
    def __init__(self, database):
        self.database = database

    def get_connection(self):
        return sqlite3.connect(self.database)

    def create_user_table(self):
        with self.get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users_cities (
                    user_id INTEGER NOT NULL,
                    city_id INTEGER NOT NULL,
                    UNIQUE(user_id, city_id),
                    FOREIGN KEY(city_id) REFERENCES cities(id)
                )
                """
            )

    def find_city(self, city_name):
        with self.get_connection() as conn:
            return conn.execute(
                """
                SELECT id, city, lat, lng
                FROM cities
                WHERE LOWER(city) = LOWER(?)
                LIMIT 1
                """,
                (city_name.strip(),)
            ).fetchone()

    def get_coordinates(self, city_name):
        city = self.find_city(city_name)
        if city is None:
            return None
        return city[2], city[3]

    def add_city(self, user_id, city_name):
        city = self.find_city(city_name)
        if city is None:
            return "not_found"

        city_id = city[0]

        with self.get_connection() as conn:
            existing = conn.execute(
                """
                SELECT 1
                FROM users_cities
                WHERE user_id = ? AND city_id = ?
                """,
                (user_id, city_id)
            ).fetchone()

            if existing:
                return "exists"

            conn.execute(
                """
                INSERT INTO users_cities (user_id, city_id)
                VALUES (?, ?)
                """,
                (user_id, city_id)
            )

        return "added"

    def select_cities(self, user_id):
        with self.get_connection() as conn:
            rows = conn.execute(
                """
                SELECT cities.city
                FROM users_cities
                JOIN cities ON users_cities.city_id = cities.id
                WHERE users_cities.user_id = ?
                ORDER BY cities.city
                """,
                (user_id,)
            ).fetchall()

        return [row[0] for row in rows]

    def create_map(self, path, cities):
        fig = plt.figure(figsize=(12, 7))
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.stock_img()
        ax.coastlines()

        for city_name in cities:
            city = self.find_city(city_name)
            if city is None:
                continue

            _, display_name, lat, lon = city
            ax.plot(
                lon,
                lat,
                marker="o",
                markersize=5,
                transform=ccrs.Geodetic()
            )
            ax.text(
                lon + 2,
                lat + 2,
                display_name,
                fontsize=8,
                transform=ccrs.Geodetic()
            )

        plt.tight_layout()
        plt.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)

    @staticmethod
    def haversine_distance(lat1, lon1, lat2, lon2):
        earth_radius_km = 6371.0088

        lat1, lon1, lat2, lon2 = map(
            math.radians,
            [lat1, lon1, lat2, lon2]
        )

        delta_lat = lat2 - lat1
        delta_lon = lon2 - lon1

        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1)
            * math.cos(lat2)
            * math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return earth_radius_km * c

    def calculate_distance(self, city1, city2):
        coords1 = self.get_coordinates(city1)
        coords2 = self.get_coordinates(city2)

        if coords1 is None or coords2 is None:
            return None

        return self.haversine_distance(
            coords1[0], coords1[1],
            coords2[0], coords2[1]
        )

    def create_distance_map(self, path, city1, city2):
        first = self.find_city(city1)
        second = self.find_city(city2)

        if first is None or second is None:
            raise ValueError("Mindestens eine Stadt wurde nicht gefunden.")

        _, name1, lat1, lon1 = first
        _, name2, lat2, lon2 = second

        fig = plt.figure(figsize=(12, 7))
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.stock_img()
        ax.coastlines()

        ax.plot(
            [lon1, lon2],
            [lat1, lat2],
            marker="o",
            transform=ccrs.Geodetic()
        )

        ax.text(lon1 + 2, lat1 + 2, name1, fontsize=9, transform=ccrs.Geodetic())
        ax.text(lon2 + 2, lat2 + 2, name2, fontsize=9, transform=ccrs.Geodetic())

        plt.tight_layout()
        plt.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)
