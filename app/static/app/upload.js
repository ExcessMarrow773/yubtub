function switchVideoForm() {
	title = document.getElementById("title")

	if (title.textContent == "Post Video"){
		title.textContent = "Reupload Video from Youtube"
	} else {
		title.textContent = "Post Video"
	}
}