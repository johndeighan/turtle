# mydecorators.py

import os, sys, io, functools

def do_twice(func):
	@functools.wraps(func)
	def wrapper(*args, **kwargs):
		print("<<<")
		value = func(*args, **kwargs)
		value = func(*args, **kwargs)
		print(">>>")
		return value
	return wrapper

def debug(func):
	"""Print the function signature and return value"""
	@functools.wraps(func)
	def wrapper_debug(*args, **kwargs):
		args_repr = [repr(a) for a in args]                      # 1
		kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]  # 2
		signature = ", ".join(args_repr + kwargs_repr)           # 3
		print(f"Calling {func.__name__}({signature})")
		value = func(*args, **kwargs)
		print(f"{func.__name__!r} returned {value!r}")           # 4
		return value
	return wrapper_debug

# --- Functions that are decorated with @unittest are
#     set to None, saving memory

def unittest(func):
	if sys.argv[0].find('pytest') > -1:
		return func
	else:
		return None
