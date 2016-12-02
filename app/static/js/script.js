/* 
 * Handles the front-end for searching the intersection between two actors
 * Users can input two actors and the page will return a list of the movies that contain both actors
 * Users can also input two movies and the page will return a list of the actors that acted in both movies
 */

$(document).ready(function() {

  /* Handles the sign in of a user
   * Checks the username and password and sends a GET Request
   */
  $('#signin-form').submit(function(e) {
    e.preventDefault();
    var $username = $('#username').val();
    var $password = $('#password').val();

    $.ajax({
      url: "/login/",
      type: "GET",
      data: {username: $username, password: $password},
      dataType: "html",
      success: function (result) {
        console.log(result);
        if (result == "-1")
          alert("The sign-in information is incorrect.");
        else
          window.location.href = "/"
      },
      error: function (xhr, ajaxOptions, thrownError) {
        console.log(xhr, ajaxOptions, thrownError);
      }
    });
  });

  /* Handles the registration of a new user
   * Checks the username and password and sends a GET Request
   */
  $('#register-form').submit(function(e) {
    e.preventDefault();
    var $username = $('#username').val();
    var $password = $('#password').val();

    $.ajax({
      url: "/register/",
      type: "GET",
      data: {username: $username, password: $password},
      dataType: "html",
      success: function (result) {
        console.log(result);
        if (result == "-1")
          alert("That username is already taken.");
        else
          window.location.href = "/"
      },
      error: function (xhr, ajaxOptions, thrownError) {
        console.log(xhr, ajaxOptions, thrownError);
      }
    });
  });

  /*
   * Handles the form submission for the actors form
   * Users can input two actors and get a list of cross-referenced movies
   */
  $('#actor-form').submit(function(e) {
    e.preventDefault(); // Prevents the form from being submitted as per its default action
    console.log('Default form submission was prevented.'); // For manual testing purposes
    var $firstActor = $('#first-actor').val();
    var $secondActor = $('#second-actor').val();
    $('#first-actor').val('');
    $('#second-actor').val('');
    
    // Makes the post request to the backend
    $.ajax({
      url: "/actors/",
      type: "GET",
      data: {firstActor: $firstActor, secondActor: $secondActor},
      dataType: "json",
      success: function (result) {
        console.log('GET request returned successfully.') // For manual testing purposes
        console.log(result);
        // Clears the current table body for the new search results
        $('#results-table tbody').remove();
        var $resultsBody = $('<tbody>').appendTo('#results-table');
        // There are no common movies between the actors
        if (result['commonMovies'].length == 0) {
          var $errorRow = $('<tr>', {
            'text': 'It seems like there are no movies with both of these actors.',
            'class': 'error-banner'
          }).appendTo($resultsBody);
        }
        else {
          // Loops through all the common movies and creates a table row for each
          $.each(result['commonMovies'], function(movieIndex, movie) {
            var $movieRow = $('<tr>').appendTo($resultsBody);
            var $movieCol = $('<td>', {'text': movie['title']}).appendTo($movieRow);
            var $dateCol = $('<td>', {'text': movie['date']}).appendTo($movieRow);
          });
        }
      },
      error: function (xhr, ajaxOptions, thrownError) {
        console.log(xhr, ajaxOptions, thrownError);
      }
    });
    console.log('GET request was sent successfully.'); // For manual testing purposes
  });

  /*
   * Handles the form submission for the movies form
   * Users can input two movies and get a list of the cross-referenced actors
   */
  $('#movie-form').submit(function(e) {
    e.preventDefault(); // Prevents the form from being submitted as per its default action
    console.log('Default form submission was prevented.'); // For manual testing purposes
    var $firstMovie = $('#first-movie').val();
    var $secondMovie = $('#second-movie').val();
    $('#first-movie').val('');
    $('#second-movie').val('');
    
    // Makes the post request to the backend
    $.ajax({
      url: "/movies/",
      type: "GET",
      data: {firstMovie: $firstMovie, secondMovie: $secondMovie},
      dataType: "json",
      success: function (result) {
        console.log('GET request returned successfully.') // For manual testing purposes
        console.log(result);
        // Clears the current table body for the new search results
        $('#results-table tbody').remove();
        var $resultsBody = $('<tbody>').appendTo('#results-table');
        // If there are no common actors between the two movies, return an error banner
        if (result['commonActors'].length == 0) {
          var $errorRow = $('<tr>', {
            'text': 'It seems like there are no actors that have acted in both of these movies.',
            'class': 'error-banner'
          }).appendTo($resultsBody);
        }
        else {
          // Loops through all the common actors and creates a table row for each
          $.each(result['commonActors'], function(actorIndex, actor) {
            var $actorRow = $('<tr>').appendTo($resultsBody);
            var $actorCol = $('<td>', {'text': actor['name'], 'text-align': 'center'}).appendTo($actorRow);
          });
        }
      },
      error: function (xhr, ajaxOptions, thrownError) {
        console.log(xhr, ajaxOptions, thrownError);
      }
    });
    console.log('GET request was sent successfully.'); // For manual testing purposes
  });
});