// MARK: - InterviewCardView (RTL Fixed)
// المشاكل المُصلَحة:
// 1. الـ badge يمين، المدة يسار
// 2. العنوان محاذاة يمين
// 3. الاسم والتاريخ مرتّبان RTL
// 4. النص المعاين محاذاة يمين
// 5. عدد المقاطع يمين، السهم اتجاهه صح

import SwiftUI

struct InterviewCardView: View {
    let title: String
    let guestName: String
    let date: String
    let duration: String
    let previewText: String
    let segmentsCount: Int
    let status: String // "مفرّغة" | "مسجّلة" | "منشورة"
    
    var statusColor: Color {
        switch status {
        case "مفرّغة": return .green
        case "منشورة": return .blue
        default:       return .orange
        }
    }

    var body: some View {
        VStack(alignment: .trailing, spacing: 10) {

            // ── الصف الأول: Badge يمين | المدة يسار ──
            HStack {
                // المدة — يسار
                HStack(spacing: 4) {
                    Text(duration)
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Image(systemName: "clock")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                Spacer()

                // Badge الحالة — يمين
                HStack(spacing: 4) {
                    Text(status)
                        .font(.caption2)
                        .fontWeight(.semibold)
                        .foregroundColor(statusColor)
                    Image(systemName: "checkmark.circle.fill")
                        .font(.caption2)
                        .foregroundColor(statusColor)
                }
                .padding(.horizontal, 10)
                .padding(.vertical, 4)
                .background(statusColor.opacity(0.12))
                .clipShape(Capsule())
            }

            // ── العنوان — يمين ──
            Text(title)
                .font(.headline)
                .fontWeight(.semibold)
                .frame(maxWidth: .infinity, alignment: .trailing)
                .multilineTextAlignment(.trailing)

            // ── الصف الثاني: التاريخ والاسم — RTL ──
            HStack(spacing: 6) {
                Spacer()

                // التاريخ
                HStack(spacing: 4) {
                    Text(date)
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Image(systemName: "calendar")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                Text("·")
                    .foregroundColor(.secondary)
                    .font(.caption)

                // الاسم
                HStack(spacing: 4) {
                    Text(guestName)
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Image(systemName: "person")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }

            // ── النص المعاين — يمين ──
            if !previewText.isEmpty {
                Text(previewText)
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .lineLimit(2)
                    .frame(maxWidth: .infinity, alignment: .trailing)
                    .multilineTextAlignment(.trailing)
            }

            Divider()

            // ── الصف الأخير: عدد المقاطع يمين | سهم التوسعة يسار ──
            HStack {
                // السهم — يسار (في RTL يشير لليسار = للأمام)
                Image(systemName: "chevron.left")
                    .font(.caption)
                    .foregroundColor(.secondary)

                Spacer()

                // عدد المقاطع — يمين
                HStack(spacing: 4) {
                    Text("\(segmentsCount) مقطع")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Image(systemName: "text.bubble")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding(16)
        .background(Color(.systemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 14))
        .shadow(color: .black.opacity(0.06), radius: 6, x: 0, y: 2)
        // ← ضروري: يضمن ترتيب العناصر RTL
        .environment(\.layoutDirection, .rightToLeft)
    }
}

// MARK: - Preview
#Preview {
    VStack(spacing: 12) {
        InterviewCardView(
            title: "تجربة حوار",
            guestName: "علي محمد",
            date: "25 Feb 2026",
            duration: "0:40",
            previewText: "طيب، شكراً لك.",
            segmentsCount: 5,
            status: "مفرّغة"
        )
        InterviewCardView(
            title: "لقاء",
            guestName: "محمد",
            date: "25 Feb 2026",
            duration: "0:08",
            previewText: "السلام عليكم ورحمة الله وبركاته",
            segmentsCount: 1,
            status: "مفرّغة"
        )
    }
    .padding()
    .background(Color(.systemGroupedBackground))
}
