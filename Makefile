build: clean
	pip install -r requirements.txt
	pip install pyinstaller
	pyinstaller pyetenotes.spec
	cp -r debian build/debian
	mkdir build/debian/usr/lib
	cp -r dist/pyetenotes build/debian/usr/lib/pyetenotes
	dpkg -b build/debian dist/pyetenotes_amd64.deb

install: build
	sudo dpkg -i dist/pyetenotes_amd64.deb

uninstall:
	sudo dpkg -r pyetenotes

clean:
	rm -rf dist build
