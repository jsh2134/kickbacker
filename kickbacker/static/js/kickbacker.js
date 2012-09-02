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

function save_key(key, backer_id, project_id, url, kb_url, email, kb_type) {
    $.ajax({ 'type': 'POST',
           'async': false, 
           'cache': false,
           'datatype': 'json',
           'data': {
                'key' : key,
                'backer_id' : backer_id,
                'project_id' : project_id,
                'url' : url,
                'kb_url' : kb_url,
                'email' : email,
                'kb_type': kb_type
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
  try {
    return matched[1];
  } catch(err) {
    return false;
  }
}

function get_project_id(url) {
  var pattern = '/projects/([A-z0-9]*)/?';
  var matched = url.match(pattern);
  try {
    return matched[1];
  } catch(err) {
    return false;
  }
}

function build_kb_url(project_id, backer_id, kb_type) {
  if (kb_type == 'owner') {
       return self.document.location.origin + "/" 
            + "new/"
            + project_id + "/"
  } else  {
       return self.document.location.origin + "/" 
            + "r/"
            + project_id + "/"
            + backer_id + "/"
  }
}

function clean_url(url) {
  var pattern = '([^?]*)';
  var matched = url.match(pattern);
  return matched[1]
}

function is_valid_kickstarter_url(url, url_type) {
  if (url.match('kickstarter') == null) {
    return false;
  }
  if ((url_type == 'backer') && (get_backer_id(url) == false)) {
    return false;
  }
  if ((url_type == 'project') && (get_project_id(url) == false)) {
    return false;
  }
  return true;
}

function display_url() {
    $('#go').attr('disabled', 'disabled');
    var url = $('#ks-url').val();
    var profile = $('#ks-profile').val();
    var email = $('#ks-email').val();
    var kb_type = $('#kb-type').val();

    //Strip Args from URLs
    url = clean_url(url);
    profile = clean_url(profile);

    var backer_id = get_backer_id(profile);
    var project_id = get_project_id(url);
    var kb_url = build_kb_url(project_id, backer_id, kb_type);
    get_awesm_url(kb_url, function(data) {
                $('#button-div').toggle();
                $('#your-link').toggle();
                $('#your-link-area').val(data.awesm_url);
                save_key(data.path, backer_id, project_id, url, kb_url, email, kb_type);
              }, function(data) {
                  console.log(data);
                  $('#your-link').html("An Error has occurred when shortening your url: " + data.responseText);
                  });
   }
function is_valid_email() {
  var re = /\S+@\S+\.\S+/;
  return re.test($('#ks-email').val());
}
function is_valid_submit() {
   if (is_valid_kickstarter_url($('#ks-url').val(), 'project') == false) {
     return false;
  }
   if (is_valid_kickstarter_url($('#ks-profile').val(), 'backer') == false) {
     return false;
  }
   if (is_valid_email() == false) {
     return false;
  }
  return true;
}
