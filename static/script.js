const colors = [
    ["#120318", "#1a0335"],
    ["#1a0335", "#1e0549"],
    ["#1e0549", "#27065f"],
    ["#27065f", "#120318"]
];

let step = 0;
const background = document.querySelector(".background");

function changeGradient() {
    const c1 = colors[step % colors.length][0];
    const c2 = colors[step % colors.length][1];

    background.style.background = `linear-gradient(-45deg, ${c1}, ${c2})`;
    step++;
}

setInterval(changeGradient, 5000); 
