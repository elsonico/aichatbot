function sendQuestion() {
    var question = document.getElementById('userQuestion').value;
    document.getElementById('userQuestion').disabled = true;
    fetch('https://www.auroranrunner.com:5005/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: question })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('responseArea').innerHTML += '<p><strong>You:</strong> ' + question + '</p>';
        document.getElementById('responseArea').innerHTML += '<p><strong>ChatBot:</strong> ' + data.answer + '</p>';
        document.getElementById('userQuestion').value = '';
        document.getElementById('userQuestion').disabled = false;
    })
    .catch((error) => {
        console.error('Error:', error);
        document.getElementById('responseArea').innerHTML += '<p>Error: ' + error.toString() + '</p>';
        document.getElementById('userQuestion').disabled = false;
    });
}
