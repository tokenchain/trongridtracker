#!/usr/bin/python
from typing import Tuple

from SQLiteAsJSON import ManageDB
from . import obj_to_tuple, obj_to_string
import os.path
import sqlite3
import json
import time

from SQLiteAsJSON.SQLiteAsJSON import db_logger
from lib.common.utils import folder_paths, FolderBase


class MistData(ManageDB, FolderBase):
    mist_map: str
    mist_profile: str

    def __init__(self, project_name: str):
        x = False
        self.mist_map = "mist_map"
        self.mist_profile = "mist_profile"
        self.by_project_name(project_name)
        self.data_schema = "data/sql/project_planner.json"
        path_db = os.path.join(self.cachefolder, 'cache.db')
        try:
            super().__init__(path_db, self.data_schema)
        except sqlite3.OperationalError:
            print("wrong path, so the file is not found.")
            print(path_db)
            exit(1)
        self.check_table_init()

    def check_table_init(self):
        x = False
        check_list = [self.mist_profile, self.mist_map]
        for rx in check_list:
            if self.found_table(rx) is False:
                x = True
        if x is True:
            print("database is not established")
            self.create_table()

    def has_mapping(self, address: str) -> bool:
        return self.has_the_address(self.mist_map, address)

    def has_profile(self, address: str) -> bool:
        return self.has_the_address(self.mist_profile, address)

    def has_the_address(self, table_name: str, address: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT address FROM {table_name} WHERE address = ?", (address,))
        db_result = cursor.fetchone()
        cursor.close()
        if db_result is None:
            return False
        else:
            return True

    def found_report(self, table_name: str, address: str, coin_type: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name} WHERE address = ? AND coin_type = ?", (address, coin_type,))
        db_result = cursor.fetchone()
        cursor.close()
        if db_result is None:
            return False
        else:
            return True

    def found_table(self, tableName: str) -> bool:
        sqlStatement = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tableName}'"
        cursor = self.conn.cursor()
        cursor.execute(sqlStatement)
        db_result = cursor.fetchone()
        if db_result is None:
            return False
        else:
            return True

    def _raw_json(self, table_name: str, address: str) -> dict:
        cursor = self.conn.cursor()
        data = ''
        addr_id = ''
        try:
            cursor.execute(f'SELECT address, file FROM {table_name} WHERE address = ?', (address,))
            (addr_id, data) = cursor.fetchone()

        except Exception as E:
            db_logger.error('Data Insert Error : ', E)
        _da = json.loads(data)
        return _da

    def read_mapping(self, address: str):
        if self.has_the_address(self.mist_map, address) is False:
            return False
        return self._raw_json(self.mist_map, address)

    def read_profile(self, address: str, coin_type: str):
        if self.found_report(self.mist_profile, address, coin_type) is False:
            return False
        return self._raw_json(self.mist_profile, address)

    def is_report_found(self, address: str, coin_type: str):
        return self.found_report(self.mist_map, address, coin_type)

    def is_profile_found(self, address: str, coin_type: str):
        return self.found_report(self.mist_profile, address, coin_type)

    def sync_coin_report(self, address: str, coin_type: str, file: dict) -> bool:
        if self.found_report(self.mist_map, address, coin_type) is False:
            return self.insert_mapping(address, {
                "coin_type": coin_type,
                "file": json.dumps(file)
            })
        try:
            columns = obj_to_string({
                "coin_type": coin_type,
                "file": json.dumps(file)
            })
            # update query
            self.conn.execute(f"UPDATE {self.mist_map} set {columns} where address='{address}'")

        except Exception as E:
            db_logger.error('Data Update Error : ', E)
            return False

        self.conn.commit()
        return True

    def get_map_by_address(self, address: str) -> list[Tuple]:
        sql_request = f"SELECT * FROM {self.mist_map} WHERE address='{address}'"
        cursor = self.conn.cursor()
        cursor.execute(sql_request)
        db_result = cursor.fetchall()
        return db_result

    def update_profile(self, address: str, params: dict) -> bool:
        if self.is_profile_found(address, params["coin_type"]) is False:
            return self.insert_profile(address, params)
        try:
            params["updatetime"] = round(time.time())
            columns = obj_to_string(params)
            # update query
            self.conn.execute(f"UPDATE {self.mist_profile} set {columns} where address='{address}'")
        except Exception as E:
            db_logger.error('Data Update Error : ', E)
            return False

        self.conn.commit()
        return True

    def insert_mapping(self, addr: str, params) -> bool:
        # Create UUID
        params["address"] = addr
        params["updatetime"] = round(time.time())  # Current unix time in milliseconds
        columns = obj_to_tuple(params)
        # insert query
        try:
            query = (
                f'INSERT OR IGNORE INTO {self.mist_map} ({columns["keys"]}) VALUES ({columns["values"]})'
            )
            self.conn.execute(query, params)
            self.conn.commit()
        except (
                sqlite3.OperationalError,
                Exception
        ) as e:
            db_logger.error('Data Insert Error : ', e)
            return False

        return True

    def insert_profile(self, addr: str, params) -> bool:
        # Create UUID
        params["address"] = addr
        params["updatetime"] = round(time.time())  # Current unix time in milliseconds
        columns = obj_to_tuple(params)
        # insert query
        try:
            query = (
                f'INSERT OR IGNORE INTO {self.mist_profile} ({columns["keys"]}) VALUES ({columns["values"]})'
            )
            self.conn.execute(query, params)
            self.conn.commit()
        except (
                sqlite3.OperationalError,
                Exception
        ) as e:
            db_logger.error('Data Insert Error : ', e)
            return False

        return True
