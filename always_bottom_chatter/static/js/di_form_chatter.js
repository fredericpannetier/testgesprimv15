// odoo.define('always_bottom_chatter.DiFormChatter', function(require) {
//     "use strict";
//     require('mail_enterprise/static/src/widgets/form_renderer/form_renderer.js');
//     var FormChatter = require('mail_enterprise/static/src/widgets/form_renderer/form_renderer.js');



//     var DiFormChatter = FormChatter.include({

//         _isChatterAside() {
//             const parent = this._chatterContainerTarget && this._chatterContainerTarget.parentNode;
//             return (
//                 false
//                 // config.device.size_class >= config.device.SIZES.XXL &&
//                 // !this.attachmentViewer &&
//                 // // We also test the existance of parent.classList. At start of the
//                 // // form_renderer, parent is a DocumentFragment and not the parent of
//                 // // the chatter. DocumentFragment doesn't have a classList property.
//                 // !(parent && parent.classList && parent.classList.contains('o_form_sheet'))
//             );
//         },

//         //copie standard
//         _updateChatterContainerTarget() {
//             if (this._isChatterAside()) {
//                 $(this._chatterContainerTarget).removeClass('o-aside');
//             } else {
//                 $(this._chatterContainerTarget).removeClass('o-aside');
//             }
//         },


//     });

//     return DiFormChatter;

// });