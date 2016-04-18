import {
	script,
} from 'html-dist';

export default {
	// where to write to
	outputFile: 'dist/index.html',
	// minify the HTML
	minify: true,
	body: {
		remove: 'script',
		// append the following things to the body
		appends: [
		          script({
		        	  src: 'https://cdnjs.cloudflare.com/ajax/libs/systemjs/0.19.26/system.js'
		          }),
		          script({
		        	  src: 'core.min.js'
		          }),
		          script({
		        	  contents: 'System.import("appl/main")'
		          })
		          ]
	}
}