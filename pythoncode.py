import web

urls = (
    '/users', 'list_users',
    '/users/(.*)', 'get_user'
)
app = web.application(urls, globals())

class get_user:
    def GET(self):
        return "hello"


if __name__ == "__main__":
    app.run()

# def main():
#     if len(sys.argv) == 0:
#         return ["please enter method signature"]
#     else:
#         return ["hello"]
#
# if __name__ == '__main__':
#     main()

