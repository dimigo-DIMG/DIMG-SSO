function getList2DOM(data, index) {
  const scriptElement = document.getElementById("list2DOM");
  const jinjaLocation = scriptElement.getAttribute('jinja-location');
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
  const itemIco = document.createElement("a");
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

  // Service information node creation
  const itemInfo = document.createElement("div");
  itemInfo.classList.add("item-info");

  const itemInfoHead = document.createElement("div");
  itemInfoHead.classList.add("item-info-head");

  const itemInfoTit = document.createElement("span");
  itemInfoTit.classList.add("item-info-tit");
  itemInfoTit.textContent = data["name"];

  const itemTag = document.createElement("span");
  itemTag.classList.add("item-tag");
  if (data["is_official"]) {
    itemTag.classList.add("official");
  }

  itemInfoHead.append(itemInfoTit, itemTag);

  const itemInfoDesc = document.createElement("div");
  itemInfoDesc.classList.add("item-info-desc");

  const descSpan = document.createElement("span");
  descSpan.textContent = data["description"];

  itemInfoDesc.appendChild(descSpan);

  itemInfo.append(itemInfoHead, itemInfoDesc);

  // etc. menu node creation
  const itemMenu = document.createElement("div");
  itemMenu.classList.add("item-menu");

  const serviceJoined = document.createElement("div");
  serviceJoined.classList.add("service-joined", "mb-2");

  const joinedLabel = document.createElement("span");
  joinedLabel.classList.add("d-block", "joined-label");
  joinedLabel.textContent = "가입일";

  const joinedDate = document.createElement("span");
  joinedDate.classList.add("d-block");
  joinedDate.textContent = data["join_date"]; // Assuming you have a "join_date" property in your data

  serviceJoined.append(joinedLabel, joinedDate);

  const leaveButton = document.createElement("button");
  leaveButton.type = "button";
  leaveButton.classList.add("btn", "btn-danger");
  leaveButton.textContent = "탈퇴";

  itemMenu.appendChild(serviceJoined);
  itemMenu.appendChild(leaveButton);

  // Appending nodes to the main container item
  containerItem.appendChild(itemSelect);
  containerItem.appendChild(itemIco);
  containerItem.appendChild(itemInfo);
  containerItem.appendChild(itemMenu);

  return containerItem;
}