function getList2DOM(data, index) {
  // data: List<Dict>
  // index: Number

  const scriptElement = document.getElementById("list2DOM");
  const jinjaLocation = scriptElement.getAttribute("jinja-location") || "";
  const noMenu = scriptElement.getAttribute("no-menu") ? true : false;
  const menuMessage = getMenuMsg2Kor(
    scriptElement.getAttribute("menu-message") || ""
  );
  const CSRFToken = scriptElement.getAttribute("csrf-token") || "";

  // Main container item node creation
  const containerItem = document.createElement("div");
  containerItem.classList.add("container-item");

  // Checkbox node creation
  const itemSelect = document.createElement("div");
  itemSelect.classList.add("item-select");

  const checkboxInput = document.createElement("input");
  checkboxInput.classList.add("form-check-input", "generated-checkbox");
  checkboxInput.type = "checkbox";
  checkboxInput.id = `checkbox-${index}`; // Unique identifier based on index

  itemSelect.appendChild(checkboxInput);

  // Service icon image node creation
  let itemIco;
  if (data["icon"]) {
    itemIco = document.createElement("a");
    itemIco.classList.add("item-ico");
    itemIco.href = data["main_page"];

    const imgIco = document.createElement("img");
    imgIco.width = 100;
    imgIco.height = 100;
    imgIco.alt = data["name"];

    const pathRegex = /\/icons\/(.+)/;
    const icoPath = data["icon"].match(pathRegex);
    imgIco.src = `${jinjaLocation}icons/${icoPath[1]}`;

    itemIco.appendChild(imgIco);
  }

  // Service information node creation
  const itemInfo = document.createElement("div");
  itemInfo.classList.add("item-info");
  if (data["email"]) {
    itemInfo.addEventListener(
      "click",
      () => (location.href = `/manage/user/${data["email"]}`)
    );
    itemInfo.style.cursor = "pointer";
  }

  const itemInfoHead = document.createElement("div");
  itemInfoHead.classList.add("item-info-head");

  const itemInfoTit = document.createElement("span");
  itemInfoTit.classList.add("item-info-tit");
  itemInfoTit.textContent = data["name"];

  const itemTag = document.createElement("span");
  itemTag.classList.add("item-tag");
  if (data["is_official"]) {
    itemTag.classList.add("official");
  } else if (data["tag"] === "enrol") {
    itemTag.classList.add("enrol");
  } else if (data["tag"] === "grad") {
    itemTag.classList.add("grad");
  } else if (data["tag"] === "guest") {
    itemTag.classList.add("guest");
  }

  itemInfoHead.append(itemInfoTit, itemTag);

  const itemInfoDesc = document.createElement("div");
  itemInfoDesc.classList.add("item-info-desc");

  let joinedLabel;
  if (noMenu) {
    joinedLabel = document.createElement("span");
    joinedLabel.classList.add("d-block");
    joinedLabel.textContent = `가입일: ${data["join_date"]}`;
  }

  let descSpan;
  if (data["description"]) {
    descSpan = document.createElement("span");
    descSpan.textContent = data["description"];
  } else if (data["email"]) {
    descSpan = document.createElement("address");
    descSpan.textContent = data["email"];
  }

  itemInfoDesc.append(joinedLabel || "", descSpan);

  itemInfo.append(itemInfoHead, itemInfoDesc);

  let itemMenu;
  if (!noMenu) {
    // etc. menu node creation
    itemMenu = document.createElement("div");
    itemMenu.classList.add("item-menu", "align-items-end");

    const serviceJoined = document.createElement("div");
    serviceJoined.classList.add("service-joined", "mb-2");

    const joinedLabel = document.createElement("span");
    joinedLabel.classList.add("joined-label");
    joinedLabel.textContent = "가입일";

    const joinedDate = document.createElement("span");
    joinedDate.textContent = data["join_date"]; // Assuming you have a "join_date" property in your data

    serviceJoined.append(joinedLabel, joinedDate);

    const leaveButton = document.createElement("button");
    leaveButton.type = "button";
    leaveButton.classList.add("btn", "btn-danger", "col-md-6");
    leaveButton.textContent = menuMessage;
    if (data["email"]) {
      // /manage/user
      leaveButton.addEventListener("click", () => {
        const confirmMsg = `정말로 ${menuMessage}하시겠습니까?`;
        if (confirm(confirmMsg)) {
          const formData = {
            "csrf_token": CSRFToken,
            "email": data["email"],
          }

          fetch(`/${data["email"]}/delete`, {
            method: "POST",
            headers: {'Content-Type': 'application/json'}, 
            body: JSON.stringify(formData),
          })
            .then((response) => response.json())
            .then((data) => {
              if (data["result"] === "success") {
                location.reload();
              } else {
                alert("오류가 발생했습니다. 다시 시도해주세요.");
              }
            });
        }
      });
    } else {
      //location.href = `${data["unregister_page"]}`;
      // new tab
      leaveButton.addEventListener("click", () => {
        window.open(data["unregister_page"], "_blank");
      });
    }

    itemMenu.appendChild(serviceJoined);
    itemMenu.appendChild(leaveButton);
  }

  // Appending nodes to the main container item
  containerItem.appendChild(itemSelect);
  itemIco ? containerItem.appendChild(itemIco) : null;
  containerItem.appendChild(itemInfo);
  itemMenu ? containerItem.appendChild(itemMenu) : null;

  return containerItem;
}

function getMenuMsg2Kor(msg) {
  let ret = "";
  switch (msg) {
    case "getout":
      ret = "탈퇴";
      break;
    case "ban":
      ret = "삭제";
      break;
    default:
      ret = "";
      break;
  }
  return ret;
}
