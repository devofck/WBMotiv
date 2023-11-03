import sqlite3
import time
from aiogram.types import ChatJoinRequest


class Database:
    def __init__(self) -> None:
        self.__conn = sqlite3.connect('database/database.db')
        self.__cursor = self.__conn.cursor()

    def reg_user(self, tg_id: int) -> None:
        if not self.is_user_registered(tg_id):
            self.__cursor.execute(
                "INSERT INTO users(tg_id, date) VALUES(?, ?)",
                [
                    tg_id,
                    int(time.time()),
                ]
            )
            self.__conn.commit()
        else:
            self.__cursor.execute(
                'SELECT is_deleted FROM users WHERE tg_id = ?',
                [
                    tg_id
                ]
            )
            if self.__cursor.fetchone()[0] == 1:
                self.__cursor.execute(
                    'UPDATE users SET is_deleted = 0 WHERE tg_id = ?',
                    [
                        tg_id
                    ]
                )
                self.__conn.commit()

    def add_channel(
            self,
            channel_id: int,
            title: str,
            link: str

    ) -> None:
        self.__cursor.execute(
            "INSERT INTO channels(channel_id, title, link, subs) VALUES(?,?,?,?)",
            [
                channel_id,
                title,
                link,
                0
            ]
        )
        self.__conn.commit()
        self.__conn.close()

    def is_admin(self, tg_id: int) -> bool:
        if self.is_user_registered(tg_id):
            self.__cursor.execute(
                "SELECT is_admin FROM users WHERE tg_id = ?",
                [
                    tg_id
                ]
            )
            data = self.__cursor.fetchone()
            if int(data[0]) == 0:
                return False
            return True
        else:
            return False

    def get_channel(self, channel_id):
        self.__cursor.execute(
            "SELECT * FROM channels WHERE channel_id = ?",
            [
                channel_id
            ]
        )
        if not self.__cursor.fetchall():
            return True
        return False

    def register_join_request(self, request: ChatJoinRequest):
        self.__cursor.execute(
            "INSERT INTO requests(user_id, channel_id) VALUES(?, ?)",
            [
                request.from_user.id,
                request.chat.id
            ]
        )
        self.__conn.commit()

    def get_channels_ids(self, channel_id):
        self.__cursor.execute(
            "SELECT channel_id FROM channels"
        )
        return self.__cursor.fetchone()

    def is_requested(self, channel_id, user_id):
        self.__cursor.execute(
            "SELECT * FROM requests WHERE user_id = ? AND channel_id = ?",
            [
                user_id,
                channel_id
            ]
        )

        if not self.__cursor.fetchall():
            return False
        return True

    def get_channels(self):
        self.__cursor.execute(
            'SELECT * FROM channels'
        )
        data = self.__cursor.fetchall()
        return data

    def is_user_registered(self, tg_id):
        self.__cursor.execute(
            "SELECT * FROM users WHERE tg_id = ?",
            [tg_id]
        )
        if not self.__cursor.fetchall():
            return False
        return True

    def delete_user(self, tg_id):
        self.__cursor.execute(
            'UPDATE users SET is_deleted = 1 WHERE tg_id = ?',
            [
                tg_id
            ]
        )
        self.__conn.commit()

    def increase_subs(self, channels: list):
        for channel in channels:
            if not channel[3]:
                channel[3] = 0
            self.__cursor.execute(
                "UPDATE channels SET subs = ?",
                [
                    str(int(channel[3]) + 1)
                ]
            )

        self.__conn.commit()

    def get_stat(self):
        self.__cursor.execute(
            'SELECT * FROM users'
        )
        users = self.__cursor.fetchall()
        channels = self.get_channels()
        deleted = 0
        by_day_regs = [0, 0, 0, 0]  # today, yesterday, this week, this month\
        hours_in_day = 86400
        temp = 0
        time_now = int(time.time())
        total = 0
        for user in users:
            if user[4] == 1:
                deleted += 1
            else:
                if (time_now - user[2]) <= hours_in_day:
                    by_day_regs[0] += 1
                if (time_now - user[2]) <= hours_in_day * 2:
                    temp += 1
                if (time_now - user[2]) <= hours_in_day * 7:
                    by_day_regs[2] += 1
                if (time_now - user[2]) <= hours_in_day * 30:
                    by_day_regs[3] += 1
            total += 1
        by_day_regs[1] = temp
        channel_text = ''
        for channel in channels:
            channel_text += f'{channel[1]}: {channel[3]}\n'
        return (
            [total, deleted, by_day_regs],
            [channel_text]
        )

    def get_alive(self):
        self.__cursor.execute(
            'SELECT * FROM users WHERE is_deleted = 0'
        )
        return self.__cursor.fetchall()

    def delete_channel(self, channel_id):
        self.__cursor.execute(
            "DELETE FROM channels WHERE channel_id = ?",
            [
                channel_id
            ]
        )
        self.__conn.commit()

    def delete_request(self, user_id, channel_id):
        self.__cursor.execute(
            "DELETE FROM requests WHERE user_id = ? AND channel_id = ?",
            [
                user_id,
                channel_id
            ]
        )
        self.__conn.commit()
