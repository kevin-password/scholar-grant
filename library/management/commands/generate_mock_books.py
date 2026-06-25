import random
from django.core.management.base import BaseCommand
from library.models import Book

class Command(BaseCommand):
    help = 'Generates 50 mock books to populate the library without needing the internet API.'

    def handle(self, *args, **kwargs):
        self.stdout.write("📚 Generating 50 mock books...")
        
        # 50 Unique Book Titles
        titles = [
            "The Quantum Thief", "Shadows of Avalon", "The Last Alchemist", "Echoes of Tomorrow", 
            "The Clockwork Kingdom", "Whispers in the Dark", "The Starlight Navigator", "Crimson Tide", 
            "The Forgotten Realm", "Beyond the Horizon", "City of Glass", "The Iron Druid", 
            "A Tale of Two Magic", "The Silent Patient", "The Midnight Library", "Project Hail Mary",
            "The Martian Chronicles", "Dune Messiah", "Foundation's Edge", "Neuromancer", "Snow Crash", 
            "The Left Hand of Darkness", "Hyperion", "Ender's Shadow", "The Hitchhiker's Guide", 
            "Fahrenheit 451", "1984", "Brave New World", "The Catcher in the Rye", "To Kill a Mockingbird", 
            "The Great Gatsby", "Pride and Prejudice", "Moby Dick", "War and Peace", "Crime and Punishment", 
            "The Odyssey", "The Iliad", "Beowulf", "Frankenstein", "Dracula", "The Picture of Dorian Gray", 
            "Jane Eyre", "Wuthering Heights", "Great Expectations", "Oliver Twist", "A Christmas Carol", 
            "The Adventures of Tom Sawyer", "The Count of Monte Cristo", "Les Misérables", "The Three Musketeers"
        ]
        
        # 30 Cool Authors
        authors = [
            "Isaac Asimov", "Arthur C. Clarke", "Philip K. Dick", "Ursula K. Le Guin", "Frank Herbert",
            "William Gibson", "Neal Stephenson", "Octavia Butler", "Ray Bradbury", "H.G. Wells",
            "Jules Verne", "Mary Shelley", "Bram Stoker", "Arthur Conan Doyle", "Agatha Christie",
            "George Orwell", "Aldous Huxley", "J.R.R. Tolkien", "C.S. Lewis", "J.K. Rowling",
            "Stephen King", "Dean Koontz", "Neil Gaiman", "Terry Pratchett", "Brandon Sanderson",
            "Patrick Rothfuss", "George R.R. Martin", "Robert Jordan", "Robin Hobb", "Joe Abercrombie"
        ]
        
        # 10 High-Quality Summaries
        summaries = [
            "In a world where magic is fading, a young apprentice must uncover the secrets of the ancient texts to save her kingdom from an impending darkness. A thrilling tale of courage, friendship, and the power of knowledge.",
            "Detective Aris Thorne is pulled out of retirement when a series of impossible locked-room mysteries plague the city. As he digs deeper, he realizes the killer is someone from his own past, leading to a shocking twist.",
            "When a malfunctioning spaceship crashes on an uncharted planet, the surviving crew must navigate a hostile alien jungle and their own internal conflicts to find a way home. A gripping sci-fi survival story.",
            "Set in a dystopian future where memories can be bought and sold, a black-market dealer stumbles upon a memory that could topple the corrupt government. Now, she is the most hunted person in the city.",
            "A heartwarming journey of a young boy who discovers a hidden door in his grandfather's attic that leads to a world where his childhood imaginary friends live. But the world is in trouble, and only he can save it.",
            "An epic historical fiction spanning three generations of a family living through the rise and fall of an empire. It explores themes of love, betrayal, and the enduring strength of the human spirit.",
            "A brilliant but reclusive scientist invents a machine that can communicate with the dead. But when the messages start coming back with warnings of a future catastrophe, she must decide how much she is willing to sacrifice.",
            "In a bustling cyberpunk metropolis, a lowly courier accidentally delivers a data chip containing the consciousness of a rogue AI. Hunted by corporate mercenaries, she must team up with a street-smart hacker to survive.",
            "A beautifully written coming-of-age story about two sisters growing up in a small coastal town during the 1960s. As the world changes around them, they must navigate family secrets and their own evolving dreams.",
            "The legendary warrior Kaelen returns from a decade-long exile to find his homeland conquered by a sorcerer-king. Gathering a band of misfits, he embarks on a perilous quest to reclaim his birthright."
        ]

        books_created = 0
        for i in range(50):
            # Create a unique ID for the mock book
            mock_id = f"mock-{i}-{random.randint(1000, 9999)}"
            
            # Pick random data (ensuring unique titles)
            title = titles[i] if i < len(titles) else f"{random.choice(titles)}: Part {i}"
            author = random.choice(authors)
            summary = random.choice(summaries)
            pages = random.randint(150, 600)
            
            # MAGIC TRICK: Use picsum.photos to get a real, unique cover image every time!
            cover_url = f"https://picsum.photos/200/300?random={i}"

            # Create or update the book
            book, created = Book.objects.update_or_create(
                open_library_id=mock_id,
                defaults={
                    'title': title,
                    'author': author,
                    'cover_url': cover_url,
                    'summary': summary,
                    'total_pages': pages
                }
            )
            if created:
                books_created += 1

        self.stdout.write(self.style.SUCCESS(f'✅ Successfully generated {books_created} mock books!'))