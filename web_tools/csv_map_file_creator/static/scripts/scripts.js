// This is just an example of the function below.
document.getElementById('start').onclick = function() {
    var file = document.getElementById('infile').files[0];
    if (!file) {
        console.log('No file selected.');
        return;
    }
    var maxlines = parseInt(document.getElementById('maxlines').value, 10);
    var lineno = 1;
    // readSomeLines is defined below.
    readSomeLines(file, maxlines, function(line) {
        lineArr = line.split('","').sort()
        lineArr.unshift("Not mapped")
        console.log("Line: " + (lineno++) + lineArr);
        $.getJSON('static/schemas/userdata.json', function(userschema) {
            console.log(userschema)
            new_props = {}
            for (const property in userschema.properties) {
                userschema.properties[property].enum = lineArr
                
            }
            $('form').jsonForm({
                schema: userschema,
                "form":[
                    "*",
                    {
                        "type": "button",
                        "title": "Click me",
                        "onClick": function (evt) {
                            
                            console.log($("form").serializeArray());
                            var data = "text/json;charset=utf-8," + encodeURIComponent(JSON.stringify($("form").serializeArray()));
                            $('<a href="data:' + data + '" download="data.json">download JSON</a>').appendTo('#apa');
                            console.log("!")
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
                    for (var i=0; i<errors.length; i++) {
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
    fr.onload = function() {
        // Use stream:true in case we cut the file
        // in the middle of a multi-byte character
        results += decoder.decode(fr.result, {stream: true});
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
    fr.onerror = function() {
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

function removeglyphs () {
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
  
  function getQueryVariable (variable) {
    var query = window.location.search.substring(1)
    var vars = query.split('&')
    for (var i = 0; i < vars.length; i++) {
      var pair = vars[i].split('=')
      if (pair[0] === variable) { return pair[1] }
    }
    return (false)
  }

function initForm (data) {
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
  
  function promiseForm () {
    return new Promise(function (resolve, reject) {
        $.getJSON('static/schemas/userdata.json?ref=' + Math.random(), function (data2) {
            schema = data2
          })
        .then(function () {
            $('form').jsonForm({"schema":schema})
        })
     
    })}