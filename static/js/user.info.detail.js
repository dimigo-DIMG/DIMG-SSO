function getGender2Kor(gender) {
  let ret;
  switch (gender) {
    case "male":
      ret = "남성";
      break;
    case "female":
      ret = "여성";
      break;
    default:
      ret = "성별 지정 안 됨";
      break;
  }
  return ret;
}

const UserInitInfoModule = (function () {
  const userEmailFromURL = window.location.pathname
    .split("/")
    .filter(Boolean)
    .pop();

  const pageName = document.getElementById("page-name"); // Nickname
  const pageDesc = document.getElementById("page-desc"); // Email address
  const userInfo = document.getElementById("user-info"); // User Island
  let fetchedDataPromise = null;
    
  async function fetchData() {
    if (!fetchedDataPromise) {
      fetchedDataPromise = new Promise(async (resolve, reject) => {
        try {
          const response = await fetch(
            `/api/manage/users/${userEmailFromURL}`
          );
          if (!response.ok) {
            throw new Error("Network response was not OK");
          }
          const data = await response.json();

          resolve(data);
        } catch (error) {
          console.error("Fetch error:", error);
          // Hide loading cover
          loadingCover.style.display = "none";
          reject(error);
        }
      });
    }
    return fetchedDataPromise;
  }

  async function init() {
    const data = await fetchData();

    document.title = `관리 · 유저 관리 · ${data["name"]}`;

    const ulTag = document.createElement("ul");
    const liJoinedDate = document.createElement("li");
    liJoinedDate.appendChild(
      document.createTextNode(`가입일: ${data["join_date"]}`)
    );

    let liGender;
    if (data["gender"]) {
      liGender = document.createElement("li");
      const TxtGender = getGender2Kor(data["gender"]);
      const iconGender = document.createElement("i");
      iconGender.classList.add("bi", `bi-gender-${data["gender"]}`);
      liGender.append(
        document.createTextNode(`성별: ${TxtGender}`),
        iconGender
      );
    }

    let liBirth;
    if (data["birth_date"]) {
      liBirth = document.createElement("li");
      liBirth.appendChild(
        document.createTextNode(`생일: ${data["birth_date"]}`)
      );
    }

    ulTag.append(liJoinedDate, liGender || "", liBirth || "");

    pageName.appendChild(document.createTextNode(data["name"]));
    pageDesc.appendChild(document.createTextNode(data["email"]));
    userInfo.appendChild(ulTag);
  }

  // Expose only necessary methods/properties
  return {
    init: init,
  };
})();

// Initialize the module
UserInitInfoModule.init();