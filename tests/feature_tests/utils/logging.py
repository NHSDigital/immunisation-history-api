def logging(teaser: str, kwargs_to_log: list = []):
    def deco(func):
        def wrapper(*args, **kwargs):
            print_statement = [teaser]
            if kwargs_to_log:
                print_statement += ["with params"]
                print_statement += [f"{k}={kwargs[k]}" for k in kwargs_to_log]
            print_statement += ["..."]
            print(*print_statement, end=" ")
            try:
                response = func(*args, **kwargs)
                print("✅  Success")
                return response
            except Exception as e:
                print("❌  Failure")
                raise e

        return wrapper

    return deco
