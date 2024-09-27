$(document).ready(function() {
    // Runs when the items in the inventory are clicked
    $('.item').click(function() {
        const itemId = $(this).data('item-id');
        const itemType = $(this).data('item-type');
        // Makes an AJAX request to the flask server
        $.ajax({
            type: 'POST',
            url: '/equip',
            contentType: 'application/json',
            data: JSON.stringify({ item_id: itemId, item_type:itemType }),
            success: function(response) {
                if (response.status === 'success') {
                    // Updates page to unequip the previously equipped item
                    $(`[data-item-type=${itemType}]`).removeClass('blue');
                    // Updates page to equip the new item
                    $(`[data-item-id="${itemId}"]`).addClass('blue');
                }
            },
            error: function(xhr, status, error) {
                console.error("Error equipping item:", error);
            }
        });
    });

    // Runs when a course's completion box is clicked
    $('.comp-box').click(function() {
        const courseType = $(this).data('type');
        const courseID = $(this).data('id');
        // Makes an AJAX request to the flask server
        $.ajax({
            type: 'POST',
            url: '/comp',
            contentType: 'application/json',
            data: JSON.stringify({ course_type: courseType, course: courseID }),
            success: function(response) {
                if (response.status === 'success') {
                    // Removes the course element from the page
                    $(`[data-table-id=${courseID}]`).remove();
                }
            },
            error: function(xhr, status, error) {
                console.error("Error completing course:", error);
            }
        });
    });
});