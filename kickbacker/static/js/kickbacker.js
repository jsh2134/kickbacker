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

function get_backers(url, callback, err_callback) {
    $.ajax({ 'type': 'POST',
           'async': false, 
           'success': callback,
           'error': err_callback,
           'cache': false,
           'datatype': 'json',
           'data': {
                'url': url,
           },
           'url': '/project/backers'
           });
  }

function save_key(key, backer_id, project_id, url, kb_url) {
    $.ajax({ 'type': 'POST',
           'async': false, 
           'cache': false,
           'datatype': 'json',
           'data': {
                'key' : key,
                'backer_id' : backer_id,
                'project_id' : project_id,
                'url' : url,
                'kb_url' : kb_url
           },
           'url': '/key'
           });
  }

function get_project_backers() {
    var url = $('#ks-url').val();
    get_backers(url, function(data) {
                console.log(data.id);
                console.log(data.backers);
                $('#your-link').html(data.id + ' ' + data.backers);
              }, function(data) {
                  console.log(data);
                  $('#your-link').html("An Error has occurred getting backers: " + data.responseText);
                  });

}

function get_backer_id(url) {
  var pattern = '/profile/([A-z0-9]*)/?';
  var matched = url.match(pattern);
  return matched[1]
}

function get_project_id(url) {
  var pattern = '/projects/([A-z0-9]*)/?';
  var matched = url.match(pattern);
  return matched[1]
}

function get_kb_url(project_id, backer_id) {
  return self.document.location.origin + "/" 
            + "r/"
            + project_id + "/"
            + backer_id + "/"
  }

function display_url() {
    var url = $('#ks-url').val();
    var profile = $('#ks-profile').val();
    var backer_id = get_backer_id(profile);
    var project_id = get_project_id(url);
    var kb_url = get_kb_url(project_id, backer_id);
    get_awesm_url(kb_url, function(data) {
                $('#your-link').html(data.awesm_url);
                save_key(data.path, backer_id, project_id, url, kb_url);
              }, function(data) {
                  console.log(data);
                  $('#your-link').html("An Error has occurred when shortening your url: " + data.responseText);
                  });
   }

