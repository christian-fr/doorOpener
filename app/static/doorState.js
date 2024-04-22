const controller = new AbortController()

const timeoutId = setTimeout(() => controller.abort(), 2000)

const interval = setInterval(async function () {
    // method to be executed;
    console.log('piep');
    // do something with myJson
    fetch('http://127.0.0.1:5000/api/getDoorState?actor-id=[ac0001]&api-key=9a9893b036fd1708c518467a203de7405184feff1c2eb315ee8099cd8fedab58').then(
        (data) => {
            console.log(data);
            return data;
        })
}, 2200);

//clearInterval(interval); // thanks @Luca D'Amico



