function deleteStage(stage) {
    return fetch(document.URL + "delete",
         {
             method: "POST",
             body: JSON.stringify({
                stage_id: stage,
             }),
             headers: { "X-CSRFToken": getCookie("csrftoken") }
         }
    )
}

function createStage(next_stage) {
    return fetch(document.URL + "create",
         {
             method: "POST",
             body: JSON.stringify({
                next_stage_id: next_stage,
             }),
             headers: { "X-CSRFToken": getCookie("csrftoken") }
         }
    )
}
const add_buttons = document.querySelectorAll(".stage__button_type_add")
const delete_buttons = document.querySelectorAll(".stage__button_type_delete")


for (const btn of add_buttons) {
    btn.addEventListener("click", () => {
        createStage(btn.getAttribute("stage_id"))
            .then(() => {
                setTimeout(() => {document.location.reload()}, 500);
            }
            );
    })
}
for (const btn of delete_buttons) {
    btn.addEventListener("click", () => {
        deleteStage(btn.getAttribute("stage_id"))
        .then( () => {
            setTimeout(() => {document.location.reload()}, 500);
        }
        );
    })
}

function getCookie(c_name) {
    if (document.cookie.length > 0) {
        c_start = document.cookie.indexOf(c_name + "=");
        if (c_start != -1) {
            c_start = c_start + c_name.length + 1;
            c_end = document.cookie.indexOf(";", c_start);
            if (c_end == -1) c_end = document.cookie.length;
            return unescape(document.cookie.substring(c_start,c_end));
        }
    }
    return "";
}


function openPopup(popupToOpen) {
    popupToOpen.classList.add('popup_opened');
    document.addEventListener('keydown', onEscapePressed);
}


function closePopup(popupToClose) {
    popupToClose.classList.remove('popup_opened');
    document.removeEventListener('keydown', onEscapePressed);
} 

function onEscapePressed (evt) {
    if (evt.key === "Escape") {
        const popupToClose = document.querySelector('.popup_opened');
        closePopup(popupToClose);
    }
}


const editButtons = document.querySelectorAll(".stage__button_type_edit");
const editPopup = document.querySelector('.popup');

let editingStage = -1;
let stageObject;
const closeButton = document.querySelector(".popup__close-button")
closeButton.addEventListener('click', () => {closePopup(editPopup)})

for (const btn of editButtons) {
    btn.addEventListener('click', (evt) => {
        editingStage = evt.target.getAttribute("stage_id");
        stageObject = evt.target.closest('.stage');
        openPopup(editPopup);
    }) 
}

editPopup.querySelector('.popup__form').addEventListener('submit', (evt) => {
    evt.preventDefault();

    fetch("./edit", {
        method: "POST",
        body: JSON.stringify({
            stage_id: editingStage,
            description: evt.target.description.value,
            name: evt.target.name.value,
            contacts: evt.target.contacts.value
        }),
        headers: { "X-CSRFToken": getCookie("csrftoken") }
    }).then( (res) =>{

        if (res.ok){
            closePopup(editPopup);
            setTimeout(() => {document.location.reload()}, 500);
        }
    }
    )
})

const endButtons = Array.from(document.querySelectorAll('.stage__button_type_end'))
console.log(endButtons)
endButtons.forEach((btn) => {
    btn.addEventListener('click', (evt) => {
        btn.innerText = "Завершаем..."
        fetch("./" + evt.target.getAttribute("stage_id") + "/end", {
            method: "POST",
            headers: { "X-CSRFToken": getCookie("csrftoken") }
        }).then((res) => {
            if (res.ok) {
                return res.json();
            }
            return Promise.reject(res.status);
        }).catch((err) => {
            setTimeout(() => {btn.innerText = "Ошибка..."}, 1500)
        })
        .finally((err) => {
            setTimeout(() => {btn.innerText = "Завершить этап"}, 1500)
        })
    })
})