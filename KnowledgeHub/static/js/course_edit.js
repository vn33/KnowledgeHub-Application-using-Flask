// let editItemId = null;
console.log("hello")
function editCourse(id) {
    console.log("Editing course with id:", id);
    editItemId = id;
    fetch(`/edit/${id}`)
        .then(response => response.json())
        .then(data => {
            console.log("data:", data);
            document.getElementById('course_name').value = data.course_name;
            document.getElementById('description').value = data.description;
            document.getElementById('price').value = data.price;

            // Use default image if data.course_image is null or empty
            let imageSrc = data.course_image ? `/${data.course_image}` : 'images/course_img.png';
            document.getElementById('currentCourseImage').src = imageSrc;
            document.getElementById('currentCourseImage').style.display = 'block';

            // Set the form action dynamically
            document.getElementById('editCourseForm').action = `/edit/${id}`;

            // Show the modal
            var editModal = new bootstrap.Modal(document.getElementById('editModal'));
            editModal.show();
        })
        .catch(error => {
            console.error('Error fetching course details:', error);
        });
}
document.getElementById('course_image').addEventListener('change', function (event) {
    const file = event.target.files[0]; // Get the uploaded file

    if (file) {
      const reader = new FileReader();
      reader.onload = function (e) {
        const previewImage = document.getElementById('previewCourseImage');
        previewImage.src = e.target.result; // Set preview source
        previewImage.style.display = 'block'; // Make the preview visible
      };
      reader.readAsDataURL(file); // Convert image to Data URL for preview
    } else {
      // If no file is selected, hide the preview image element
      document.getElementById('previewCourseImage').style.display = 'none';
    }
  });
  