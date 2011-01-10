/*
 * Bespin wrapper
 */
/*
 * Class: Bespin.js
 * Extension for Editor to use Bespin
 */

Class.refactor(FDEditor, {
	options: {
		type: null
	},
	initialize: function(options) {
		this.previous(options);
	},
	initEditor: function(editor_id) {
		var self = this;
		this.editor_id = editor_id || this.options.element;
		this.element = $(this.editor_id);
        if (this.element) {
          // register element's content
          fd.editor_contents[this.editor_id] = this.element.get('text')
          // mark hidden elements and record initial state
          if (this.options.activate) { 
              $log('FD: activate {element}'.substitute(this.options));
              if (fd.bespinLoaded) {
                  this.show();
              } else {
                  fd.addEvent('bespinLoad', function() {
                      self.show();
                  });
              }
          } else {
              self.hidden = true; 
          }
          this.element.hide();
        } else {
          self.hidden = true;
        }
		fd.addEvent('bespinChange', function() {
			if (fd.current_editor == self.editor_id) {
				if (!fd.switching) {
					self.fireEvent('change');
					self.changed = true;
				}
			}
		});
	},

	getContent: function() {
		// this.textarea.set('text', this.bespin.value);
		if (fd.current_editor == this.editor_id) {
			return fd.bespin.getContent();
		} else {
          return fd.editor_contents[this.editor_id];
		}
	},

	setContent: function(value) {
		this.previous(value);	
		fd.bespin.setContent(value);
	},

	hide: function() {
		// if (fd.bespin) fd.editor_contents[this.element.get('id')] = fd.bespin.value;
		return this;
	},

	destroy: function() {
		this.element.destroy();
	},

	show: function() {
		// set content of the bespin
		fd.switching = true;
		fd.switchBespinEditor(this.editor_id, this.options.type);
		
		fd.switching = false;
		return this;
	},
	cleanUp: $empty
});
