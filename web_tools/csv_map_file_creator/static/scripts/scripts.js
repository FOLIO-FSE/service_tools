
window.currentschema = 'static/schemas/userdata.json'
document.addEventListener('click', function (event) {

	// If the clicked element doesn't have the right selector, bail
	if (!event.target.matches('.set_schema') || event.target.matches('.disabled') ) return;

	// Don't follow the link
  event.preventDefault();
  document.getElementById('section2').scrollIntoView()

	// Log the clicked element in the console
  $(".set_schema").removeClass('active');  
  var dataAttribute = event.target.getAttribute('data-schema-file');
  window.currentschema = dataAttribute
  event.target.classList.add("active")
  console.log(dataAttribute + "Is now the current schema");

}, false);

document.getElementById('start').onclick = function () {
  var file = document.getElementById('infile').files[0];
  if (!file) {
    alert('No file selected.');
    return;
  }
  var maxlines = parseInt(document.getElementById('maxlines').value, 10);
  var lineno = 1;
  // readSomeLines is defined below.
  readSomeLines(file, maxlines, function (line) {
    enums = line.split('","').sort()
    enums.unshift("Not mapped")
    console.log("Line: " + (lineno++) + enums);
    $.getJSON(window.currentschema, function (userschema) {
      new_props = {}
      console.log(userschema)
      addEnumsToProperties(userschema, enums)
      console.log(userschema)
      $('form').html("")
      $('form').jsonForm({
        schema: userschema,
        "form": [
          "*",
          {
            "type": "button",
            "title": "Next",
            "htmlClass":"btn btn-primary mb-2",

            "onClick": function (evt) {
              console.log($("form").serializeArray());
              myarr = $("form").serializeArray()
              myarr.forEach( obj => renameKey( obj, 'name', 'folio_field' ) );
              myarr.forEach( obj => renameKey( obj, 'value', 'legacy_field' ) );
              var data = "text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(myarr));

              document.getElementById("apa").html = ""
              $('<a class="btn btn-primary mb2" href="data:' + data + '" download="data.json">Download Mapping File</a>').appendTo('#apa');
              console.log("!")
              document.getElementById('section4').scrollIntoView(true)
              evt.preventDefault();
            }
          }
        ],
        onSubmit: function (errors, values) {
          console.log(values);
          if (errors) {
            $('#res').html('<p>I beg your pardon?</p>');
          }
          else {
            $('#res').html('<p>Hello ' + values.name + '.' +
              (values.age ? '<br/>You are ' + values.age + '.' : '') +
              '</p>');
          }
          return;
        },
        "displayErrors": function (errors, formElt) {
          for (var i = 0; i < errors.length; i++) {
            errors[i].message = "Avast! Ye best be fixin' that field!";
          }
          $(formElt).jsonFormErrors(errors, formObject);
        }
      });
    });
  }, function onComplete() {
    console.log('Read all lines');
  });

};

/**
 * Read up to and including |maxlines| lines from |file|.
 *
 * @param {Blob} file - The file to be read.
 * @param {integer} maxlines - The maximum number of lines to read.
 * @param {function(string)} forEachLine - Called for each line.
 * @param {function(error)} onComplete - Called when the end of the file
 *     is reached or when |maxlines| lines have been read.
 */
function readSomeLines(file, maxlines, forEachLine, onComplete) {
  var CHUNK_SIZE = 50000; // 50kb, arbitrarily chosen.
  var decoder = new TextDecoder();
  var offset = 0;
  var linecount = 0;
  var linenumber = 0;
  var results = '';
  var fr = new FileReader();
  fr.onload = function () {
    // Use stream:true in case we cut the file
    // in the middle of a multi-byte character
    results += decoder.decode(fr.result, { stream: true });
    var lines = results.split('\n');
    results = lines.pop(); // In case the line did not end yet.
    linecount += lines.length;

    if (linecount > maxlines) {
      // Read too many lines? Truncate the results.
      lines.length -= linecount - maxlines;
      linecount = maxlines;
    }

    for (var i = 0; i < lines.length; ++i) {
      forEachLine(lines[i] + '\n');
    }
    offset += CHUNK_SIZE;
    seek();
  };
  fr.onerror = function () {
    onComplete(fr.error);
  };
  seek();

  function seek() {
    if (linecount === maxlines) {
      // We found enough lines.
      onComplete(); // Done.
      return;
    }
    if (offset !== 0 && offset >= file.size) {
      // We did not find all lines, but there are no more lines.
      forEachLine(results); // This is from lines.pop(), before.
      onComplete(); // Done
      return;
    }
    var slice = file.slice(offset, offset + CHUNK_SIZE);
    fr.readAsArrayBuffer(slice);
  }
}


function addEnumsToProperties(myObject, enums) {  
  if(myObject != null && "$ref" in myObject){
    console.log("ref")
    delete myObject["$ref"]
  }    
  for (property in myObject.properties) {
    if(myObject.properties[property] != null && "$ref" in myObject.properties[property]){
      console.log("ref")
      delete myObject.properties[property]
    }      
    else if(["metadata", "meta", "tags", "proxyFor"].includes(property)){
      console.log(property)
      delete myObject.properties[property]
    }
    //console.log(JSON.stringify(myObject.properties[property]))   
    else if (myObject.properties[property]['type'] == "object") {
      addEnumsToProperties(myObject.properties[property], enums)
    }
    else if (myObject.properties[property]['type'] == "array") {
      addEnumsToProperties(myObject.properties[property]["items"], enums)
    }
    else {
      myObject.properties[property]["type"] = "string"
      myObject.properties[property].enum = enums
      if ("format" in myObject.properties[property]) {
        delete myObject.properties[property]["format"]
      }
    }

  }
}

function removeglyphs() {
  // Select the node that will be observed for mutations
  var targetNode = document.getElementById('formDiv')

  // Options for the observer (which mutations to observe)
  var config = { attributes: true, childList: true, subtree: true }

  // Callback function to execute when mutations are observed
  var callback = function (mutationsList, observer) {
    var els = document.getElementsByClassName('glyphicon-plus-sign')

    var sliced = Array.prototype.slice.call(els)
    var i
    for (i = 0; i < sliced.length; i++) {
      sliced[i].className = 'fa text-info fa-plus-square-o fa-2x'
    }
    els = document.getElementsByClassName('glyphicon-minus-sign')

    sliced = Array.prototype.slice.call(els)

    for (i = 0; i < sliced.length; i++) {
      sliced[i].className = 'fa text-info fa-minus-square-o fa-2x'
    }
    observer.disconnect()
  }

  // Create an observer instance linked to the callback function
  var observer = new MutationObserver(callback)

  // Start observing the target node for configured mutations
  observer.observe(targetNode, config)
}

function getQueryVariable(variable) {
  var query = window.location.search.substring(1)
  var vars = query.split('&')
  for (var i = 0; i < vars.length; i++) {
    var pair = vars[i].split('=')
    if (pair[0] === variable) { return pair[1] }
  }
  return (false)
}

function initForm(data) {
  var schema
  $.when(
    $.getJSON('static/schemas/userdata.json?ref=' + Math.random(), function (data2) {
      schema = data2
    })
  ).then(function () {
    console.log(schema)
    if (schema) {
      $('form').jsonForm({
        schema: schema,
        onSubmit: function (errors, values) {
          if (errors) {
            alert(JSON.stringify(errors))
          } else {
            var data = JSON.stringify(values)
            var newPath = '/api/any' + window.location.pathname
            $.ajax({
              url: newPath,
              type: window.location.pathname.includes('/create') ? 'POST' : 'PUT',
              data: data,
              success: function (result) {
                $('#postAlertSuccess').show()
                $('#postAlertError').hide()
                $('#postAlertSuccess1').show()
                $('#postAlertError1').hide()
              },
              error: function (xhr, ajaxOptions, thrownError) {
                $('#postAlertError').show()
                $('#postAlertSuccess').hide()
                $('#postAlertError1').show()
                $('#postAlertSuccess1').hide()
              }
            })
          }
        }
      })
    }
  })
  return data
}

function promiseForm() {
  return new Promise(function (resolve, reject) {
    $.getJSON('static/schemas/userdata.json?ref=' + Math.random(), function (data2) {
      schema = data2
    })
      .then(function () {
        $('form').jsonForm({ "schema": schema })
      })

  })
}

function isArray(what) {
  return Object.prototype.toString.call(what) === '[object Array]';
}

function isNested(obj) {
  for (var i = 1; i < arguments.length; i++) {
    if (!obj.hasOwnProperty(arguments[i])) {
      return false;
    }
    obj = obj[arguments[i]];
  }
  return true;
}

function removeClass(){
  for (var i = 0; i < elements.length; i++) {
    elements[i].classList.remove('active');
  }
}

function renameKey ( obj, oldKey, newKey ) {
  obj[newKey] = obj[oldKey];
  delete obj[oldKey];
}
