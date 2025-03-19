import json
import os
import time
import logging
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from PresentationHandler import handling
import sys
from Logging import time_logger, error_logger, gemini_logger , process_logger

# Add the root directory of your project to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..', '..')))



def create_presentation(service, title):
    """
    Create a new Google Slides presentation and return its ID.
    """
    body = {'title': title}
    presentation = service.presentations().create(body=body).execute()
    return presentation['presentationId']

def add_slides_with_content(service, presentation_id, json_file):
    """
    Add slides with content from the provided JSON file to the presentation.
    """
    with open(json_file, 'r') as f:
        data = json.load(f)

    slides = data.get('slides', [])
    chapter_number = data.get('chapter', 'Unknown')
    chapter_title = data.get('title', 'Untitled Chapter')
    book_name = data.get('book_name', 'Unknown Book')

    # Get the first slide's ID
    presentation = service.presentations().get(presentationId=presentation_id).execute()
    first_slide_id = presentation['slides'][0]['objectId']

    # Create the text box for Chapter Number
    chapter_number_request = {
        'createShape': {
            'objectId': 'ChapterNumberText',
            'shapeType': 'TEXT_BOX',
            'elementProperties': {
                'pageObjectId': first_slide_id,
                'size': {
                    'width': {'magnitude': 6000000, 'unit': 'EMU'},
                    'height': {'magnitude': 1500000, 'unit': 'EMU'}
                },
                'transform': {
                    'scaleX': 1,
                    'scaleY': 1,
                    'translateX': 3000000,  # Center horizontally
                    'translateY': 1000000,  # Vertical position
                    'unit': 'EMU'
                }
            }
        }
    }

    # Insert the Chapter Number text
    insert_chapter_number_text = {
        'insertText': {
            'objectId': 'ChapterNumberText',
            'text': f"Chapter {chapter_number}",
            'insertionIndex': 0
        }
    }

    # Style the Chapter Number text
    style_chapter_number_text = {
        'updateTextStyle': {
            'objectId': 'ChapterNumberText',
            'textRange': {
                'type': 'ALL'  # Apply to all text
            },
            'style': {
                'bold': True,
                'fontSize': {
                    'magnitude': 50,  # Font size in points
                    'unit': 'PT'
                },
                'foregroundColor': {  # Add text color
                    'opaqueColor': {
                        'rgbColor': {
                            'red': 0.0,
                            'green': 0.0,
                            'blue': 0.0
                        }
                    }
                }
            },
            'fields': 'bold,fontSize,foregroundColor'
        }
    }

    # Create the text box for Chapter Title
    chapter_title_request = {
        'createShape': {
            'objectId': 'ChapterTitleText',
            'shapeType': 'TEXT_BOX',
            'elementProperties': {
                'pageObjectId': first_slide_id,
                'size': {
                    'width': {'magnitude': 9000000, 'unit': 'EMU'},
                    'height': {'magnitude': 1000000, 'unit': 'EMU'}
                },
                'transform': {
                    'scaleX': 1,
                    'scaleY': 1,
                    'translateX': 100000,  # Center horizontally
                    'translateY': 2000000,  # Vertical position below chapter number
                    'unit': 'EMU'
                }
            }
        }
    }

    # Insert the Chapter Title text
    insert_chapter_title_text = {
        'insertText': {
            'objectId': 'ChapterTitleText',
            'text': chapter_title,
            'insertionIndex': 0
        }
    }

    # Style and Align Chapter Title Text
    style_chapter_title_text = {
        'updateTextStyle': {
            'objectId': 'ChapterTitleText',
            'textRange': {'type': 'ALL'},
            'style': {
                'bold': False,
                'fontSize': {'magnitude': 36, 'unit': 'PT'}
            },
            'fields': 'bold,fontSize'
        }
    }
    align_chapter_title_text = {
        'updateParagraphStyle': {
            'objectId': 'ChapterTitleText',
            'textRange': {'type': 'ALL'},
            'style': {'alignment': 'CENTER'},
            'fields': 'alignment'
        }
    }

    # Book Name Text Box
    book_name_request = {
        'createShape': {
            'objectId': 'BookNameText',
            'shapeType': 'TEXT_BOX',
            'elementProperties': {
                'pageObjectId': first_slide_id,
                'size': {
                    'width': {'magnitude': 9000000, 'unit': 'EMU'},
                    'height': {'magnitude': 1000000, 'unit': 'EMU'}
                },
                'transform': {
                    'scaleX': 1,
                    'scaleY': 1,
                    'translateX': 100000,  # Bottom-left corner
                    'translateY': 4000000,  # Near bottom of the slide
                    'unit': 'EMU'
                }
            }
        }
    }
    insert_book_name_text = {
        'insertText': {
            'objectId': 'BookNameText',
            'text': book_name,
            'insertionIndex': 0
        }
    }
    style_Book_Name_text = {
        'updateTextStyle': {
            'objectId': 'BookNameText',
            'textRange': {'type': 'ALL'},
            'style': {
                'bold': True,
                'fontSize': {'magnitude': 18, 'unit': 'PT'},
                'foregroundColor': {
                    'opaqueColor': {
                        'rgbColor': {'red': 0.0, 'green': 0.0, 'blue': 0.0}
                    }
                }
            },
            'fields': 'bold,fontSize,foregroundColor'
        }
    }

    # Combine all requests
    all_requests = [
        chapter_number_request,
        insert_chapter_number_text,
        style_chapter_number_text,
        chapter_title_request,
        insert_chapter_title_text,
        style_chapter_title_text,
        align_chapter_title_text,
        book_name_request,
        insert_book_name_text,
        style_Book_Name_text,
    ]

    service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': all_requests}
    ).execute()

    for slide_number, slide in enumerate(slides, start=1):
        title = slide.get('title', 'Untitled Slide')
        content = slide.get('content', [])

        # Enforce bullet point constraints
        # Ensure 4 to 7 bullets and truncate each to 50 characters
        if len(content) > 7:
            content = content[:]
        content = [bullet[:] for bullet in content]

        # Combine the bullet points into a single string for Google Slides
        formatted_content = '\n'.join([f"• {bullet}" for bullet in content])

        # Create a new slide
        create_slide_request = {
            'createSlide': {
                'slideLayoutReference': {
                    'predefinedLayout': 'TITLE_AND_BODY'
                }
            }
        }
        response = service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': [create_slide_request]}
        ).execute()

        # Get the new slide's ID
        new_slide_id = response['replies'][0]['createSlide']['objectId']

        # Retrieve slide placeholders
        presentation = service.presentations().get(presentationId=presentation_id).execute()
        slide_elements = next(
            (s['pageElements'] for s in presentation['slides'] if s['objectId'] == new_slide_id), None
        )

        title_id = None
        body_id = None
        for element in slide_elements:
            placeholder = element.get('shape', {}).get('placeholder', {})
            if placeholder.get('type') == 'TITLE':
                title_id = element['objectId']
            elif placeholder.get('type') == 'BODY':
                body_id = element['objectId']

        if not title_id or not body_id:
            error_logger.error(f"Placeholders for TITLE or BODY not found for slide {new_slide_id}. Skipping this slide.")
            continue

        # Add title, bullet points, and footer to the slide
        requests = [
            {
                'insertText': {
                    'objectId': title_id,
                    'text': title,
                    'insertionIndex': 0
                }
            },
            {
                'insertText': {
                    'objectId': body_id,
                    'text': formatted_content,
                    'insertionIndex': 0
                }
            },
            {
                'createShape': {
                    'objectId': f'SlideNumberFooter_{slide_number}',
                    'shapeType': 'TEXT_BOX',
                    'elementProperties': {
                        'pageObjectId': new_slide_id,
                        'size': {
                            'width': {'magnitude': 9000000, 'unit': 'EMU'},
                            'height': {'magnitude': 100000, 'unit': 'EMU'}
                        },
                        'transform': {
                            'scaleX': 1,
                            'scaleY': 1,
                            'translateX': 100000,  # Center horizontally
                            'translateY': 4750000,  # Near the bottom of the slide
                            'unit': 'EMU'
                        }
                    }
                }
            },
            {
                'insertText': {
                    'objectId': f'SlideNumberFooter_{slide_number}',
                    'text': f"{slide_number}",
                    'insertionIndex': 0
                }
            },
            {
                'updateTextStyle': {
                    'objectId': f'SlideNumberFooter_{slide_number}',
                    'textRange': {'type': 'ALL'},
                    'style': {
                        'fontSize': {'magnitude': 12, 'unit': 'PT'},
                        'foregroundColor': {
                            'opaqueColor': {
                                'rgbColor': {'red': 0.0, 'green': 0.0, 'blue': 0.0}
                            }
                        }
                    },
                    'fields': 'fontSize,foregroundColor'
                }
            },
            {
                'updateParagraphStyle': {
                    'objectId': f'SlideNumberFooter_{slide_number}',
                    'textRange': {'type': 'ALL'},
                    'style': {'alignment': 'CENTER'},
                    'fields': 'alignment'
                }
            }
        ]
        service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()

def create_presentation_for_chapter(service, drive_service, chapter_number, book_name, template_id):
    #json_file = os.path.join('ppt_jsons', f'chapter_{chapter_number}.json')
    json_file =os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))), 'pdf-summarizer/ppt_jsons', book_name ,f'chapter_{chapter_number}.json')  
    retry_count = 0
    max_retries = 4  # Increase the number of retries
    while retry_count < max_retries:
        try:
            # Copy the template presentation
            copied_presentation = drive_service.files().copy(
                fileId=template_id,
                body={'name': f'Chapter {chapter_number} - {book_name}'}
            ).execute()
            presentation_id = copied_presentation['id']

            # Add slides from JSON
            add_slides_with_content(service, presentation_id, json_file)

            # Make the presentation public
            handling.make_presentation_public(drive_service, presentation_id)

            # Store the public link
            return f"https://docs.google.com/presentation/d/{presentation_id}/edit"
        except Exception as e:
            #print(f"An error occurred while processing {json_file}: {e}")
            error_logger.error(f"Error processing {json_file}: {e}")
            retry_count += 1
            if retry_count < max_retries:
                process_logger.info(f"Retrying {json_file} ({retry_count}/{max_retries})...")
                time.sleep(20)  # Wait for 60 seconds before retrying
            else:
                process_logger.info(f"Failed to process {json_file} after {max_retries} retries.")
                return None