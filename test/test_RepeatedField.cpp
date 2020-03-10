/*
 *  Copyright (C) 2020 Embedded AMS B.V. - All Rights Reserved
 *
 *  This file is part of Embedded Proto.
 *
 *  Embedded Proto is open source software: you can redistribute it and/or 
 *  modify it under the terms of the GNU General Public License as published 
 *  by the Free Software Foundation, version 3 of the license.
 *
 *  Embedded Proto  is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with Embedded Proto. If not, see <https://www.gnu.org/licenses/>.
 *
 *  For commercial and closed source application please visit:
 *  <https://EmbeddedProto.com/license/>.
 *
 *  Embedded AMS B.V.
 *  Info:
 *    info at EmbeddedProto dot com
 *
 *  Postal adress:
 *    Johan Huizingalaan 763a
 *    1066 VH, Amsterdam
 *    the Netherlands
 */

#include <gtest/gtest.h>

#include <Fields.h>
#include <RepeatedField.h>

namespace test_EmbeddedAMS_RepeatedField
{

TEST(RepeatedField, construction) 
{
  static constexpr uint32_t SIZE = 3;
  EmbeddedProto::RepeatedFieldSize<::EmbeddedProto::uint32, SIZE> x;
}

TEST(RepeatedField, size_uint32_t) 
{  
  static constexpr uint32_t SIZE = 3;
  EmbeddedProto::RepeatedFieldSize<::EmbeddedProto::uint32, SIZE> x;

  static constexpr int32_t UINT32_SIZE = sizeof(::EmbeddedProto::uint32);

  EXPECT_EQ(0, x.get_size());
  EXPECT_EQ(SIZE*UINT32_SIZE, x.get_max_size());
  EXPECT_EQ(0, x.get_length());
  EXPECT_EQ(SIZE, x.get_max_length());

  x.add(1);
  x.add(2);
  EXPECT_EQ(2*UINT32_SIZE, x.get_size());
  EXPECT_EQ(2, x.get_length());

  x.add(3);

  EXPECT_EQ(SIZE*UINT32_SIZE, x.get_size());
  EXPECT_EQ(SIZE*UINT32_SIZE, x.get_max_size());
  EXPECT_EQ(SIZE, x.get_length());
  EXPECT_EQ(SIZE, x.get_max_length());
}

TEST(RepeatedField, set) 
{
  static constexpr uint32_t SIZE = 3;
  EmbeddedProto::RepeatedFieldSize<::EmbeddedProto::uint32, SIZE> x;

  // First add a value in the middle and see if we have a size of two.
  x.set(1, 2);
  EXPECT_EQ(2, x.get(1));
  EXPECT_EQ(2, x.get_length());

  x.set(0, 1);
  EXPECT_EQ(1, x.get(0));

  x.set(2, 3);
  EXPECT_EQ(3, x.get(2));
}

} // End namespace test_EmbeddedAMS_RepeatedField