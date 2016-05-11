build:
	- rm -rf dist
	mkdir dist
	./node_modules/.bin/jspm bundle appl/main dist/appl.js
	./node_modules/.bin/uglifyjs dist/appl.js -o dist/appl.min.js
	./node_modules/.bin/html-dist --config html-dist.config.js --input index.html
	mkdir -p dist/jspm_packages/github/twbs/"bootstrap@3.3.6"/fonts
	cp -r jspm_packages/github/twbs/"bootstrap@3.3.6"/fonts/* dist/jspm_packages/github/twbs/"bootstrap@3.3.6"/fonts/
	mkdir -p dist/jspm_packages/npm/font-awesome@4.6.1/fonts
	cp -r jspm_packages/npm/font-awesome@4.6.1/fonts/* dist/jspm_packages/npm/font-awesome@4.6.1/fonts/
	
	cp favicon.ico dist/
	cp config.js dist/
	cat dist/config.js dist/appl.min.js > dist/core.min.js
	./node_modules/.bin/jspm unbundle