function get_awesm_url(url, callback, err_callback) {
    var aws_key = '5c8b1a212434c2153c2f2c2f2c765a36140add243bf6eae876345f8fd11045d9';
    var aws_app = 'mKU7uN';
    $.ajax({ 'type': 'POST',
           'async': false, 
           'success': callback,
           'error': err_callback,
           'cache': false,
           'datatype': 'json',
           'data': {
                'v': '3',
                'key': aws_key,
                'tool': aws_app,
                'url': url,
                'channel': 'email',
                'format': 'json'
           },
           'url': 'http://api.awe.sm/url'
           });
  }

function display_url() {
    var url = $('#ks-url').val();
    get_awesm_url(url, function(data) {
                $('#your-link').html(data.awesm_url);
              }, function(data) {
                  console.log(data);
                  $('#your-link').html("An Error has occurred when shortening your url: " + data.responseText);
                  });
   }

