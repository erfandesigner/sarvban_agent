import os
import hashlib
from django.core.management.base import BaseCommand
from support.models import RagDocument, hash_chunk
from support.services.embeddings import embed_texts


class Command(BaseCommand):
    help = "Ingest RAG documents (read → chunk → embed → save, skip duplicates)"

    def add_arguments(self, parser):
        parser.add_argument("folder", type=str)

    def handle(self, *args, **opts):
        folder = opts["folder"]

        if not os.path.isdir(folder):
            self.stdout.write(self.style.ERROR(f"Folder not found: {folder}"))
            return

        self.stdout.write(self.style.NOTICE(f"Scanning folder: {folder}"))

        # خواندن و embedding
        records = embed_texts(folder, batch_size=32)

        if not records:
            self.stdout.write(self.style.WARNING("No documents found to ingest."))
            return

        self.stdout.write(self.style.NOTICE(f"Preparing {len(records)} chunks for DB..."))

        objs = []
        file_stats = {}
        duplicate_count = 0

        for r in records:
            source = r["metadata"]["source"]
            file_stats.setdefault(source, {"chunks": 0, "skipped": 0})

            chunk_hash = hash_chunk(r["chunk"])

            # بررسی تکرار قبل از ذخیره
            if RagDocument.objects.filter(source_id=source, chunk_hash=chunk_hash).exists():
                file_stats[source]["skipped"] += 1
                duplicate_count += 1
                continue

            file_stats[source]["chunks"] += 1
            objs.append(
                RagDocument(
                    source_id=source,
                    title=r["metadata"]["title"],
                    chunk=r["chunk"],
                    embedding=r["embedding"],
                    metadata=r["metadata"],
                    chunk_hash=chunk_hash,
                )
            )

        # ذخیره یک‌باره
        RagDocument.objects.bulk_create(objs, batch_size=200, ignore_conflicts=True)

        # گزارش
        self.stdout.write(self.style.NOTICE("Ingestion report:"))
        for f, stat in file_stats.items():
            self.stdout.write(
                f"- {os.path.basename(f)} → stored {stat['chunks']} chunks "
                f"(skipped {stat['skipped']} duplicates)"
            )

        self.stdout.write(self.style.SUCCESS(
            f"Ingested {len(objs)} new chunks, skipped {duplicate_count} duplicates "
            f"from {len(file_stats)} files."
        ))
