def handle(image):
    from core.models import Controller, ControllerImages, Image
    from collections import defaultdict

    if (image.kind == "container"):
        # container images do not get instantiated
        return

    controller_images = ControllerImages.objects.filter(image=image)
    existing_controllers = [cs.controller for cs in controller_images] 
    
    all_controllers = Controller.objects.all() 
    for controller in all_controllers:
        if controller not in existing_controllers:
            sd = ControllerImages(image=image, controller=controller)
            sd.save()

