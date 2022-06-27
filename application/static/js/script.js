function loadDeck(username, kid_id, deck_id) {
  $.ajax({
    url: `/api/${username}/${kid_id}/${deck_id}`,
    type: "POST",
    dataType: "json",
    success: function (data) {
      $(page_content).replaceWith(data);
    },
  });
}

function playAudio(audioPath) {
  audio_file = new Audio(audioPath);
  audio_file.play();
}
