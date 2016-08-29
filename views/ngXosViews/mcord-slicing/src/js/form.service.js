/**
 * © OpenCORD
 *
 * Visit http://guide.xosproject.org/devguide/addview/ for more information
 *
 * Created by teone on 9/29/16.
 */

(function () {
  'use strict';
  angular.module('xos.mcord-slicing')
  .service('FormHandler', function(LabelFormatter, XosFormHelpers){
    const self = this;
    const t = d3.transition()
      .duration(500);

    // draw a form nearby the node
    this.drawForm = (node, linkGroup, formGroup) => {

      // create an svg to draw a line from the node to the form
      const line = linkGroup
        .append('line')
        .attr({
          class: 'form-line',
          id: `form-line-${node.type}-${node.id}`,
          x1: node.x + 10,
          y1: node.y,
          x2: node.x + 10,
          y2: node.y + 40,
          opacity: 0,
        });

      line.transition(t)
        .attr({
          opacity: 1
        });

      // form container
      const form = formGroup
        .append('div')
        .attr({
          class: 'element-form',
          id: `form-${node.type}-${node.id}`,
        })
        .style({
          opacity: 0
        });

      const formEl = form
        .append('form');

      // cicle trough props (to be defined from rest)
      this.addFormfields(node, formEl);

      const buttonRow = formEl
        .append('div')
        .attr({
          class: 'row'
        });

      buttonRow
        .append('div')
        .attr({
          class: 'col-xs-6'
        })
        .append('a')
        .attr({
          class: 'btn btn-danger',
          'data-parent-node-type': node.type,
          'data-parent-node-id': node.id
        })
        .text('Close')
        .on('click', function(){
          self.removeForm(
            d3.select(this).attr('data-parent-node-type'),
            d3.select(this).attr('data-parent-node-id'),
            linkGroup,
            formGroup
          );
        });

      buttonRow
        .append('div')
        .attr({
          class: 'col-xs-6'
        })
        .append('button')
        .attr({
          type: 'button',
          class: 'btn btn-success'
        })
        .text('Save')
        .on('click', function(){
          $(`#form-${node.type}-${node.id} input`).each(function(){
            let input = $(this); // This is the jquery object of the input, do what you will
            let val = input.val();
            let name = input.attr('name');
            console.log(name, val);
          });
        });

      form.transition(t)
        .style({
          opacity: 1,
          top: `${node.y + 95}px`,
          left: `${node.x}px`
        });
    };

    this.removeForm = (nodeType, nodeId, linkGroup, formGroup) => {
      this.removeFormByParentNode({type: nodeType, id: nodeId}, linkGroup, formGroup);
    };

    // remove a form starting form his parent node
    this.removeFormByParentNode = (node, linkGroup, formGroup) => {
      // remove form
      formGroup.selectAll(`#form-${node.type}-${node.id}`)
        .transition(t)
        .style({
          opacity: 0
        })
        .remove();
      // remove link
      linkGroup.selectAll(`#form-line-${node.type}-${node.id}`)
        .transition(t)
        .attr({
          opacity: 0
        })
        .remove();
    };

    this.getFieldValue = (val, fieldType) => {
      if(fieldType === 'date'){
        val = new Date(val);
        val = `${val.getFullYear()}-${('0' + val.getMonth() + 1).slice(-2)}-${('0' + val.getDate()).slice(-2)}`
      }
      return val || '';
    };

    this.addFormField = (fieldName, fieldValue, formEl) => {
      let fieldType = XosFormHelpers._getFieldFormat(fieldValue);
      formEl
        .append('div')
        .attr({
          class: 'row'
        })
        .append('div')
        .attr({
          class: 'col-xs-12'
        })
        .append('label')
        .text(fieldName ? LabelFormatter.format(fieldName ) : 'test')
        .append('input')
        .attr({
          type: fieldType,
          name: fieldName,
          value: this.getFieldValue(fieldValue, fieldType),
          class: 'form-control'
        });
    };

    this.addFormfields = (node, formEl) => {

      this.addFormField('name', node.name, formEl);
      // tmp check
      if(!node.model){
        return this.addFormField(null, null, formEl);
      }

      // create a list of fields to be printed
      const fields = Object.keys(node.model);
      _.forEach(fields, f => {
        this.addFormField(f, node.model[f], formEl);
      });
    };
  });
})();

