.PHONY: bootstrap pack clean

bootstrap: bootstrap.py
	./boot.sh

clean:
	rm -f bootstrap.py virtualenv.py *.pyc testsuite/*.pyc

virtualenv.py:
	wget https://raw.github.com/pypa/virtualenv/master/virtualenv.py

bootstrap.py: virtualenv.py
	./genbootstrap.py