function deleteCourse(id) { 
    deleteItemId = id;
    $('#confirmDeleteModal').modal('show');
    console.log("Checking confirmDeleteButton:", $('#confirmDeleteButton').length);
}

$(document).on('click', '#confirmDeleteButton', function() {
    console.log("Delete button clicked");  // Debugging log

    if (deleteItemId !== null) {
        console.log("Attempting to delete course with ID:", deleteItemId);
        const url = `/delete/${deleteItemId}`;

        fetch(url, {
            method: 'DELETE',
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(response => response.json())
        .then(data => {
            if (data.redirect) {
                // First hide the modal...
                $('#confirmDeleteModal').modal('hide');
                // Optionally wait a brief moment before redirecting
                setTimeout(() => {
                    window.location.href = data.redirect;
                }, 300);
            } else {
                console.error("No redirect URL provided.");
            }
        })
        .catch(error => console.error("Fetch error:", error));
    }
});
