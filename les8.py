from instabot import Bot
import os
import dotenv


class InstaChain:
    users = {}
    bot = Bot()

    def __init__(self, user1, user2, max_depth, login, password):
        self.user1 = user1
        self.user2 = user2
        self.max_depth = max_depth
        self.login = login
        self.password = password

    def run(self):
        self.bot.login(username=self.login, password=self.password)
        user1_id = self.bot.get_user_id_from_username(self.user1)
        user2_id = self.bot.get_user_id_from_username(self.user2)
        self.users.update({user1_id: {'parent': None, 'depth': 0}})
        self._find_friends(user2_id, self.max_depth)
        return self._find_chain(user2_id)

    def _find_friends(self, user2_id, max_depth, depth=1):
        found = False
        tmp_dict = {}
        for key, value in self.users.items():
            if found:
                break
            if value['depth'] == depth - 1:
                user1_followers = self.bot.get_user_followers(key)
                user1_following = self.bot.get_user_following(key)
                user1_friends = list(set(user1_followers) & set(user1_following))
                for friend in user1_friends:
                    if not self.users.get(friend):
                        tmp_dict.update({friend: {'parent': key, 'depth': depth}})
                    if friend == user2_id:
                        found = True
                        break
        self.users.update(tmp_dict)
        if (depth != max_depth) and not found:
            self._find_friends(user2_id, max_depth, depth=depth + 1)

    def _find_chain(self, user2_id):
        result = []
        if not self.users.get(user2_id):
            depth = self.users.get(user2_id)['depth']
            user_id = user2_id
            while True:
                user_name = self.bot.get_username_from_user_id(user_id)
                result.append(user_name)
                user_id = self.users.get(user_id)['parent']
                depth -= 1
                if depth == -1:
                    break
        return result


if __name__ == "__main__":
    dotenv.load_dotenv(".env")
    user1 = os.getenv("USER1")
    user2 = os.getenv("USER2")
    chain = InstaChain(
        user1,
        user2,
        4,
        login=os.getenv("INST_LOGIN"),
        password=os.getenv("INST_PSWORD")
    )
    print(chain.run())
