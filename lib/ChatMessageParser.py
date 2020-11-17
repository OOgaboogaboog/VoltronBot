import re
from datetime import datetime, timezone, timedelta

from lib.common import get_broadcaster, get_db

class ChatMessageParser:
	def __init__(self, chat_string, event=None):
		self.variables = {
			'sender': self.sender,
			'uptime': self.uptime,
			'count': self.counter,
		}

		self.chat_string = chat_string
		self.event = event
		self._twitch_api = None
		self._broadcaster = None

	def parse(self):
		all_vars = re.findall(r'\{([^ ]+)\}', self.chat_string)
		vars = []
		[vars.append(x) for x in all_vars if x not in vars]
		parsed_str = self.chat_string

		for v in vars:
			split = v.split(':')
			key = split[0]
			args = split[1:]
			if key in self.variables:
				res = self.variables[key](self.event, *args)
				if res:
					parsed_str = parsed_str.replace(f'{{{v}}}', res)

		return parsed_str

	def sender(self, event, *args):
		if not event:
			return None

		return event.display_name

	def uptime(self, event, *args):
		if not self.broadcaster:
			return None

		stream_info = self.twitch_api.get_stream(self.broadcaster.twitch_user_id)

		if not stream_info:
			return None

		started_at = datetime.strptime(stream_info['started_at'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone(timedelta(0)))
		now = datetime.utcnow().replace(tzinfo=timezone(timedelta(0)))
		secs = (now - started_at).total_seconds()

		hours, rem = divmod(secs, 3600)
		minutes, rem = divmod(rem, 60)

		return f'{hours:.0f} hours {minutes:.0f} minutes'

	def counter(self, event, *args):
		if len(args) > 1:
			return None

		counter_name = args[0]

		con, cur = get_db()

		sql = "SELECT id, value FROM counters WHERE counter_name = ?"
		cur.execute(sql, (counter_name,))

		res = cur.fetchone()

		count = 1
		if not res:
			sql = "INSERT INTO counters (counter_name, value) VALUES (?, 1)"
			cur.execute(sql, (counter_name, ))
			count = 1
		else:
			count = res['value'] + 1
			sql = "UPDATE counters SET value = ? WHERE id = ?"
			cur.execute(sql, (count, res['id']))

		con.commit()
		con.close()

		return str(count)

	@property
	def twitch_api(self):
		if not self._twitch_api:
			if not self.broadcaster:
				return None
			self._twitch_api = self.broadcaster.twitch_api
		return self._twitch_api

	@property
	def broadcaster(self):
		if not self._broadcaster:
			self._broadcaster = get_broadcaster()
		return self._broadcaster