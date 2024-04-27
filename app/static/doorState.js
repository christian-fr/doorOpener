function setState() {
    const apiKey = $('#api-key').value;
    const actorId = $('#actor-id').value;
    fetch('./api/setState', {
    method: 'POST',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({"api-key": apiKey, "actor-id": actorId})
  }).then(response => {
        if (!response.ok) {
            console.log("error");
        }
        console.log("success");
    })
}


